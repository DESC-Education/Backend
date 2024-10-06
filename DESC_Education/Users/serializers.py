from rest_framework import serializers
from Users.models import CustomUser
from Chats.models import Chat, Message
from django.db.models import Subquery, OuterRef, Count, Q
from Notifications.serializers import NotificationSerializer
from Notifications.models import Notification
from django.utils import timezone


class CustomUserSerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(source="is_active")
    isStaff = serializers.BooleanField(source="is_staff")
    isSuperuser = serializers.BooleanField(source="is_superuser")
    createdAt = serializers.DateTimeField(source="created_at")
    isVerified = serializers.BooleanField(source="is_verified")
    unreadChatsCount = serializers.SerializerMethodField()
    notifications = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "email", "role", "isActive", "isStaff", "isSuperuser",
                  'isVerified', 'createdAt', 'unreadChatsCount', 'notifications']

    def get_notifications(self, obj) -> NotificationSerializer(many=True):
        queryset = Notification.objects.filter(user=obj,
                                               created_at__gte=(timezone.now() - timezone.timedelta(days=7)))

        return NotificationSerializer(queryset, many=True).data

    def get_unreadChatsCount(self, obj) -> int:
        return Message.objects.filter(is_readed=False).filter(Q(chat__members=obj) & ~Q(user=obj))\
            .aggregate(Count('chat', distinct=True)).get('chat__count')


class EmptySerializer(serializers.Serializer):
    empty = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)


class RegistrationSerializer(serializers.Serializer):
    STUDENT_ROLE = "student"
    COMPANY_ROLE = "company"

    ROLE_CHOISES = [
        (STUDENT_ROLE, "Student Role"),
        (COMPANY_ROLE, "Company Role")
    ]

    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    role = serializers.ChoiceField(choices=ROLE_CHOISES, default=STUDENT_ROLE)


class VerifyRegistrationSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    email = serializers.EmailField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class VerifyCodeSerializer(serializers.Serializer):
    REGISTRATION_TYPE = "RG"
    PASSWORD_CHANGE_TYPE = "PW"
    EMAIL_CHANGE_TYPE = "EM"

    TYPE_CHOISES = [
        (REGISTRATION_TYPE, "Registration Code"),
        (PASSWORD_CHANGE_TYPE, "Password Code"),
        (EMAIL_CHANGE_TYPE, "Email Code")
    ]

    type = serializers.CharField(max_length=2)
    email = serializers.EmailField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    email = serializers.EmailField()
    new_password = serializers.CharField(max_length=128, write_only=True)


class ChangeEmailSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class TestDeleteSerializer(serializers.Serializer):
    email = serializers.EmailField()
