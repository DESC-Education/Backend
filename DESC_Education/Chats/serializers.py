from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from Users.models import CustomUser
from Chats.models import (
    Chat,
    Message,
    ChatMembers
)
from Tasks.models import (
    Task
)
from django.db.models import Q, Count

from Files.models import File
from Files.serializers import FileSerializer


class WebSocketSerializer(serializers.Serializer):
    MESSAGE = 'message'
    FILE = 'file'
    VIEWED = 'viewed'
    CHOISES = [
        (MESSAGE, 'Сообщение'),
        (VIEWED, 'Отметка о прочтении'),
        (FILE, 'Файл')
    ]
    id = serializers.UUIDField(required=False)
    type = serializers.ChoiceField(choices=CHOISES, default=MESSAGE)
    payload = serializers.JSONField(required=False)


class SendFileSerializer(FileSerializer):
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), required=True, write_only=True)

    class Meta(FileSerializer.Meta):
        fields = FileSerializer.Meta.fields + ('chat',)

    def validate(self, attrs):
        user = self.context['request'].user
        chat = attrs.get('chat')
        if not chat.chatmembers_set.filter(user=user).exists():
            raise serializers.ValidationError({'chat': 'Данный чат не найден'})

        attrs['content_object'] = attrs.pop('chat')
        return super().validate(attrs)


class CompanionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'avatar']

    def get_avatar(self, obj):
        profile = obj.get_profile()
        logo = profile.logo_img
        if not logo:
            return None
        else:
            return logo.url

    def get_name(self, obj):
        profile = obj.get_profile()
        if obj.role == CustomUser.COMPANY_ROLE:
            return profile.company_name
        else:
            return f"{profile.first_name} {profile.last_name}"


class ChatTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title']


class MessageSerializer(serializers.ModelSerializer):
    user = CompanionSerializer()
    createdAt = serializers.DateTimeField(source='created_at')
    isRead = serializers.BooleanField(source='is_readed')
    files = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'message', 'user', 'createdAt', 'isRead', 'files']

    def get_files(self, obj) -> FileSerializer(many=True):
        return FileSerializer(obj.files, many=True).data


class ChatDetailSerializer(serializers.ModelSerializer):
    companion = serializers.SerializerMethodField()
    task = ChatTaskSerializer()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['companion', 'task', 'messages']

    def get_companion(self, obj) -> CompanionSerializer:
        members = obj.members.all()
        if members.count() > 1:
            current_user = self.context['request'].user
            companion = members.exclude(id=current_user.id).first()
            return CompanionSerializer(companion).data if companion else None
        return None

    def get_messages(self, obj) -> MessageSerializer(many=True):
        request = self.context['request']
        message_id = request.query_params.get('messageId')
        limit = int(request.query_params.get('page_size', 50))  # значение по умолчанию 50

        if message_id is None:
            messages = Message.objects.filter(chat=obj).order_by('-created_at')[:limit]
        else:
            try:
                reference_message = Message.objects.get(id=message_id, chat=obj)
                messages = Message.objects.filter(chat=obj, created_at__lt=reference_message.created_at) \
                               .order_by('-created_at')[:limit]
            except Message.DoesNotExist:
                messages = []

        return MessageSerializer(messages, many=True).data


class ChatListSerializer(serializers.ModelSerializer):
    lastMessage = serializers.SerializerMethodField()
    companion = serializers.SerializerMethodField()
    task = ChatTaskSerializer()
    isFavorite = serializers.SerializerMethodField()
    unreadCount = serializers.SerializerMethodField()


    class Meta:
        model = Chat
        fields = ['id', 'lastMessage', 'companion', 'task', 'isFavorite',
                  'unreadCount']

    def get_unreadCount(self, obj) -> int:
        request = self.context['request']
        user = request.user
        queryset = obj.message_set.filter(Q(is_readed=False) and ~Q(user=user))
        return queryset.count()

    def get_isFavorite(self, obj) -> bool:
        request = self.context['request']
        user = request.user
        chat_member = obj.chatmembers_set.filter(user=user, chat=obj).first()
        if chat_member.is_favorite is None:
            return False
        else:
            return True

    @staticmethod
    def get_lastMessage(obj) -> MessageSerializer:
        last_message = obj.message_set.order_by('-created_at').first()
        return MessageSerializer(last_message).data if last_message else None

    def get_companion(self, obj) -> CompanionSerializer:
        # Получаем собеседника (предполагаем, что у чата два участника)
        members = obj.members.all()
        if members.count() > 1:
            current_user = self.context['request'].user
            companion = members.exclude(id=current_user.id).first()
            return CompanionSerializer(companion).data if companion else None
        return None


class ChatChangeFavoriteSerializer(ChatListSerializer):
    chatId = serializers.UUIDField(write_only=True)

    class Meta(ChatListSerializer.Meta):
        fields = ChatListSerializer.Meta.fields + ['chatId']








class ChatSerializer(serializers.ModelSerializer):
    companionId = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),
                                                     required=True, write_only=True)
    taskId = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), source='task',
                                                required=False, write_only=True)

    companion = serializers.SerializerMethodField(read_only=True)
    task = ChatTaskSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'companionId', 'taskId', 'companion', 'task']

    def create(self, validated_data):
        self.user = validated_data.pop('user', None)
        self.companion = validated_data.pop('companionId')
        task = validated_data.get('task')


        queryset = Chat.objects.filter(Q(chatmembers__user=self.user) and Q(chatmembers__user=self.companion), task=task)

        if queryset.exists():
            return queryset.first()


        instance = Chat.objects.create(**validated_data)

        ChatMembers.objects.create(user=self.user, chat=instance)
        ChatMembers.objects.create(user=self.companion, chat=instance)


        return instance


    def validate(self, attrs):
        user = self.context['request'].user

        if user.role == CustomUser.STUDENT_ROLE:
            if not attrs.get('task'):
                raise serializers.ValidationError({'taskId': 'Это поле обязательно!'})
            if attrs.get('companionId').id != attrs.get('task').user.id:
                raise serializers.ValidationError({'taskId': 'Это поле несоответствует вашему собеседнику!'})

        if attrs.get('companionId').role == CustomUser.COMPANY_ROLE and user.role == CustomUser.COMPANY_ROLE:
            raise serializers.ValidationError({'companionId': 'Вы не можете добавлять компанию в чат!'})

        return super().validate(attrs)

    def get_companion(self, obj) -> CompanionSerializer:
        serializer = CompanionSerializer(instance=self.companion)
        return serializer.data
