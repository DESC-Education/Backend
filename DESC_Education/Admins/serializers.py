import random
from django.db.models import Count, Q
from rest_framework import serializers
from Profiles.serializers import (
    GetStudentProfileSerializer,
    GetCompanyProfileSerializer
)
from Profiles.models import (
    ProfileVerifyRequest,
    StudentProfile,
    CompanyProfile,
)
from Users.models import CustomUser


class ProfileVerifyRequestDetailSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False, max_length=255)
    status = serializers.ChoiceField(choices=ProfileVerifyRequest.STATUS_CHOICES, required=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    profile = serializers.SerializerMethodField(read_only=True)
    verificationFiles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProfileVerifyRequest
        fields = ['id', 'createdAt', 'status', 'comment', 'admin', 'profile', 'verificationFiles']
        read_only_fields = ['id', 'createdAt', 'admin']

    def validate(self, attrs):
        status = attrs.get('status')
        comment = attrs.get('comment')

        if status == ProfileVerifyRequest.REJECTED and not comment:
            raise serializers.ValidationError({"comment": "Требуется указать причину отказа!"})

        return attrs

    @staticmethod
    def get_verificationFiles(obj) -> list[str]:
        res = []
        objects = obj.profile.verification_files.all()
        for file in objects:
            res.append(file.file.url)

        return res

    @staticmethod
    def get_profile(obj) -> GetStudentProfileSerializer:
        if isinstance(obj.profile, StudentProfile):
            return GetStudentProfileSerializer(obj.profile).data
        elif isinstance(obj.profile, CompanyProfile):
            return GetCompanyProfileSerializer(obj.profile).data
        else:
            return None


class ProfileVerifyRequestsListSerializer(serializers.ModelSerializer):
    userType = serializers.CharField(source="profile.user.role")
    firstName = serializers.CharField(source="profile.first_name")
    lastName = serializers.CharField(source="profile.last_name")
    email = serializers.CharField(source="profile.user.email")
    createdAt = serializers.DateTimeField(source="created_at")
    requestStatus = serializers.CharField(source="status")

    class Meta:
        model = ProfileVerifyRequest
        fields = ['id', 'createdAt', 'requestStatus', 'comment', 'admin', "userType", "firstName", "lastName", "email"]


class CustomUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = '__all__'

    def get_profile(self, obj):
        obj.get_profile()


class CustomUserListSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at")
    lastLogin = serializers.DateTimeField(source="last_login")
    isActive = serializers.BooleanField(source="is_active")
    isSuperuser = serializers.BooleanField(source="is_superuser")
    isVerified = serializers.BooleanField(source="is_verified")
    firstName = serializers.SerializerMethodField()
    lastName = serializers.SerializerMethodField()
    companyName = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['createdAt', 'id', 'email', 'createdAt', 'lastLogin', 'isActive', 'isSuperuser', 'isVerified',
                  'firstName', 'lastName', 'role', 'companyName']


    def to_representation(self, instance):

        return super().to_representation(instance)
    @staticmethod
    def get_firstName(obj):
        return obj.get_profile().first_name

    @staticmethod
    def get_companyName(obj):
        if obj.role != CustomUser.COMPANY_ROLE:
            return None
        return obj.get_profile().company_name

    @staticmethod
    def get_lastName(obj):
        return obj.get_profile().last_name
