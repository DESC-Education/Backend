from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery, Max
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from Settings.permissions import IsCompanyRole, IsStudentRole, EvaluateCompanyRole, IsCompanyOrStudentRole
from Chats.serializers import (
    ChatSerializer,
    ChatListSerializer,
    ChatDetailSerializer,
)
from Chats.models import (
    Chat,
    Message,
)


# Create your views here.


def index(request):
    return render(request, "Chats/index.html")


def room(request, room_name):
    return render(request, "Chats/room.html", {"room_name": room_name})


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
        return Chat.objects.annotate(last_message_time=Subquery(last_message_time)).order_by('-last_message_time')

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
            OpenApiParameter(name='message_id', type=OpenApiTypes.UUID,),
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
