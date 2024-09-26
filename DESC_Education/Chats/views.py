from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from Settings.permissions import IsCompanyRole, IsStudentRole, EvaluateCompanyRole, IsCompanyOrStudentRole
from Chats.serializers import (
    ChatSerializer
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


