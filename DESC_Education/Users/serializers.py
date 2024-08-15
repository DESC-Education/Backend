from rest_framework import serializers
from Users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    # lastLogin = serializers.CharField(source="last_login")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    isActive = serializers.BooleanField(source="is_active")
    isStaff = serializers.BooleanField(source="is_staff")
    isSuperuser = serializers.BooleanField(source="is_superuser")

    class Meta:
        model = CustomUser
        fields = ["id", "email", "firstName", "lastName", "isActive", "isStaff", "isSuperuser"]


class EmptySerializer(serializers.Serializer):
    email = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)


class VerifyRegistrationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)
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
