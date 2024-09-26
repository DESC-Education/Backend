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


class ChatTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title']


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
            return logo.path

    def get_name(self, obj):
        profile = obj.get_profile()
        if obj.role == CustomUser.COMPANY_ROLE:
            return profile.company_name
        else:
            return f"{profile.first_name} {profile.last_name}"


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

    def get_companion(self, obj):
        serializer = CompanionSerializer(instance=self.companion)
        return serializer.data
