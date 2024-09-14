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


class ProfileVerifyRequestDetailSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at")
    profile = serializers.SerializerMethodField()
    verificationFiles = serializers.SerializerMethodField()

    class Meta:
        model = ProfileVerifyRequest
        fields = ['id', 'createdAt', 'status', 'comment', 'admin', 'profile', 'verificationFiles']

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
