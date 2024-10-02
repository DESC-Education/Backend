from rest_framework import serializers
from Notifications.models import Notification
from Chats.models import Message, Chat
from django.db.models import Q, Count, Sum
from Users.models import CustomUser

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class MessageNotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    unreadChatCount = serializers.SerializerMethodField(read_only=True)
    message = serializers.CharField(read_only=True)
    chat = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = ['chat', 'message', 'createdAt', 'unreadChatCount', 'user']

    def get_chat(self, obj):
        return obj.chat.id

    def get_unreadChatCount(self, obj):
        user = self.validated_data.get('user')
        queryset = Message.objects.filter(is_readed=False)
        if user:
            return queryset.filter(Q(chat__members=user) and ~Q(user=user))\
                .aggregate(Count('chat', distinct=True)).get('chat__count')
        return None
