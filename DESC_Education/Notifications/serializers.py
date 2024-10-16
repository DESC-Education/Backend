from rest_framework import serializers
from Notifications.models import Notification
from Chats.models import Message, Chat
from django.db.models import Q, Count, Sum
from Users.models import CustomUser


class NotificationSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at")
    isRead = serializers.BooleanField(source="is_read")

    class Meta:
        model = Notification
        fields = ['createdAt', 'isRead', 'user', 'id', 'type', 'title', 'message', 'payload']


class MessageNotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    unreadChatsCount = serializers.SerializerMethodField(read_only=True)
    unreadCount = serializers.SerializerMethodField(read_only=True)
    message = serializers.CharField(read_only=True)
    chat = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'message', 'createdAt', 'unreadChatsCount', 'unreadCount', 'user']

    @staticmethod
    def get_chat(obj):
        return obj.chat.id

    def get_queryset(self):
        user = self.validated_data.get('user')
        if hasattr(self, 'queryset'):
            return self.queryset
        else:
            self.queryset = Message.objects.filter(is_readed=False).filter(Q(chat__members=user) & ~Q(user=user))
            return self.queryset

    def get_unreadCount(self, obj) -> int:
        queryset = self.get_queryset()
        return queryset.filter(chat=obj.chat).count()

    def get_unreadChatsCount(self, obj) -> int:
        user = self.validated_data.get('user')
        queryset = self.get_queryset()
        print(user)
        if user:
            res = queryset.aggregate(Count('chat', distinct=True)).get('chat__count')
            print(res)
        return None
