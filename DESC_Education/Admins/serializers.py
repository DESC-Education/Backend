import random
from django.db.models import Count, Q
from rest_framework import serializers
from Tasks.models import (
    TaskCategory,
    Task,
    Solution,
    Review,
    FilterCategory,
    Filter
)
from Profiles.serializers import (
    GetStudentProfileSerializer,
    GetCompanyProfileSerializer
)
from Profiles.models import (
    ProfileVerifyRequest,
    StudentProfile,
    CompanyProfile,
)
from Profiles.serializers import (
    GetStudentProfileSerializer,
    GetCompanyProfileSerializer
)
from Users.models import CustomUser
from Users.serializers import CustomUserSerializer


class StatisticsTasksSerializer(serializers.Serializer):
    fromDate = serializers.DateField(required=False, write_only=True)
    toDate = serializers.DateField(required=False, write_only=True)
    date = serializers.DateField(read_only=True)
    created = serializers.IntegerField(read_only=True)
    completed = serializers.IntegerField(read_only=True)
    pending = serializers.IntegerField(read_only=True)
    failed = serializers.IntegerField(read_only=True)


class StatisticsUserSerializer(serializers.Serializer):
    fromDate = serializers.DateField(required=False, write_only=True)
    toDate = serializers.DateField(required=False, write_only=True)
    date = serializers.DateField(read_only=True)
    students = serializers.IntegerField(read_only=True)
    companies = serializers.IntegerField(read_only=True)


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


class CustomUserListSerializer(CustomUserSerializer):
    firstName = serializers.SerializerMethodField()
    lastName = serializers.SerializerMethodField()
    companyName = serializers.SerializerMethodField()
    profileVerification = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + \
                 ['firstName', 'lastName', 'companyName', 'profileVerification']

    @staticmethod
    def get_profileVerification(obj):
        return obj.get_profile().verification

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


class CustomUserDetailSerializer(CustomUserListSerializer):
    profile = serializers.SerializerMethodField()

    class Meta(CustomUserListSerializer.Meta):
        fields = CustomUserListSerializer.Meta.fields + \
                 ['profile', ]

    def get_profile(self, obj):
        profile = obj.get_profile()
        if obj.role == CustomUser.COMPANY_ROLE:
            return GetCompanyProfileSerializer(profile).data
        elif obj.role == CustomUser.STUDENT_ROLE:
            return GetStudentProfileSerializer(profile).data


class AdminTaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'


class AdminFilterCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterCategory
        fields = '__all__'


class AdminFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'
