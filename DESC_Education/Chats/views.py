from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery, Max, F, Value
from django.db.models.functions import Coalesce
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from Files.models import File
from django.utils import timezone
from django.shortcuts import get_object_or_404
from Settings.permissions import IsCompanyRole, IsStudentRole, EvaluateCompanyRole, IsCompanyOrStudentRole
from Chats.serializers import (
    ChatSerializer,
    ChatListSerializer,
    ChatDetailSerializer,
    SendFileSerializer,
    ChatChangeFavoriteSerializer,
)
from Chats.models import (
    Chat,
    Message,
    ChatMembers
)


# Create your views here.


def index(request):
    return render(request, "Chats/index.html")


def room(request, chat_id):
    return render(request, "Chats/room.html", {"chat_id": chat_id})


class CreateChatView(generics.GenericAPIView):
    serializer_class = ChatSerializer
    permission_classes = (IsCompanyRole | IsStudentRole,)

    @extend_schema(
        tags=["Chats"],
        summary="Создание чата"
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatListView(generics.ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatListSerializer
    permission_classes = (IsCompanyRole | IsStudentRole,)

    def get_queryset(self):
        last_message_time = Message.objects.filter(chat=OuterRef('pk')).order_by('-created_at').values('created_at')[:1]
        return (Chat.objects.filter(
            chatmembers__user=self.request.user)
                    .annotate(last_message_time=Subquery(last_message_time),
                              is_favorite=Subquery(ChatMembers.objects.filter(chat=OuterRef('pk'),
                                                                              user=self.request.user)
                                                   .values('is_favorite')[:1]))
                    .order_by(F('is_favorite').desc(nulls_last=True), F('last_message_time').desc(nulls_last=True)))


    @extend_schema(
        tags=["Chats"],
        summary="Получение списка чатов"
    )
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatDetailSerializer
    permission_classes = (IsCompanyRole | IsStudentRole,)

    def get_object(self):
        chat_id = self.kwargs.get('pk')  # Получаем ID чата из URL параметров
        instance = generics.get_object_or_404(Chat, pk=chat_id)

        if not instance.chatmembers_set.filter(user=self.request.user).exists():
            self.permission_denied(self.request, message="Данный чат не найден", code=404)
        return instance

    @extend_schema(
        tags=["Chats"],
        summary="Получение detail экземпляра чата",
        parameters=[
            OpenApiParameter(name='messageId', type=OpenApiTypes.UUID, description='Для получения предыдущих '
                                                                                   'сообщений необходимо указать '
                                                                                   'последний известный id сообщения '),
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class SendFileView(generics.GenericAPIView):
    permission_classes = (IsCompanyRole | IsStudentRole,)
    serializer_class = SendFileSerializer

    @extend_schema(
        tags=["Chats"],
        summary="Отправка файла в чат",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(type=File.CHAT_FILE)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatChangeFavoriteView(ChatListView):
    permission_classes = (IsCompanyRole | IsStudentRole,)
    serializer_class = ChatListSerializer

    def get_object(self):
        chat_id = self.kwargs.get('pk')
        instance = generics.get_object_or_404(Chat, pk=chat_id)

        chat_member = instance.chatmembers_set.filter(user=self.request.user)
        if not chat_member.exists():
            self.permission_denied(self.request, message="Данный чат не найден", code=404)
        return chat_member.first()

    @extend_schema(
        tags=["Chats"],
        summary="Добавление/удаления чата из favorite",
    )
    def get(self, request, pk, *args, **kwargs):
        member: ChatMembers = self.get_object()
        if member.is_favorite is None:
            member.is_favorite = timezone.now()
        else:
            member.is_favorite = None
        member.save()

        return super().get(request, pk, *args, **kwargs)
