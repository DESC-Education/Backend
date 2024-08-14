from rest_framework import serializers


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
