import random
from django.db.models import Count, Q
from rest_framework import serializers

from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    BaseProfile,
    File,
    Skill,
    University,
    Faculty,
    City,
    Specialty,
    PhoneVerificationCode
)

from Tasks.models import (
    Task,
    TaskCategory,
    Solution
)


class SendPhoneCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerificationCode
        fields = ('phone',)


class SetPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerificationCode
        fields = ('phone', 'code')


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file',)


class UniversitySerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = University
        fields = "__all__"


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name',)


class BaseProfileSerializer(serializers.ModelSerializer):
    phoneVisibility = serializers.BooleanField(source="phone_visibility", required=True)
    emailVisibility = serializers.BooleanField(source="email_visibility", required=True)
    phone = serializers.CharField(read_only=True)
    firstName = serializers.CharField(source="first_name", required=True)
    lastName = serializers.CharField(source="last_name", required=True)
    telegramLink = serializers.URLField(source="telegram_link", required=False)
    vkLink = serializers.URLField(source="vk_link", required=False)
    logoImg = serializers.ImageField(source="logo_img", read_only=True)
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all(), required=True)
    verification = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BaseProfile
        fields = ('id', 'firstName', 'lastName', 'description', 'phone', 'phoneVisibility', 'emailVisibility',
                  'logoImg', 'telegramLink', 'vkLink', 'timezone', 'city', 'skills', 'verification')
        read_only_fields = ['id', 'user']

    @staticmethod
    def get_verification(obj) -> str:
        return obj.get_verification_status()


class StudentProfileSerializer(BaseProfileSerializer):
    formOfEducation = serializers.CharField(source="form_of_education", required=True)
    admissionYear = serializers.IntegerField(source="admission_year", required=True)
    university = serializers.PrimaryKeyRelatedField(queryset=University.objects.all(), required=True)
    faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all(), required=True)
    specialty = serializers.PrimaryKeyRelatedField(queryset=Specialty.objects.all(), required=True)

    class Meta(BaseProfileSerializer.Meta):
        model = StudentProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('formOfEducation', 'university', 'faculty', 'admissionYear',
                  'specialty', 'profession')


class EditStudentProfileSerializer(BaseProfileSerializer):
    phoneVisibility = serializers.BooleanField(source="phone_visibility", required=False)
    emailVisibility = serializers.BooleanField(source="email_visibility", required=False)
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all(), required=True)

    class Meta:
        model = StudentProfile
        fields = ("skills", 'phoneVisibility', 'emailVisibility', 'telegramLink', 'vkLink', 'description', 'profession')


class CreateCompanyProfileSerializer(BaseProfileSerializer):
    linkToCompany = serializers.URLField(source="link_to_company")
    companyName = serializers.CharField(source="company_name")

    class Meta(BaseProfileSerializer.Meta):
        model = CompanyProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('linkToCompany', 'companyName',)


class EditCompanyProfileSerializer(BaseProfileSerializer):
    linkToCompany = serializers.URLField(source="link_to_company", required=False)
    phoneVisibility = serializers.BooleanField(source="phone_visibility", required=False)
    emailVisibility = serializers.BooleanField(source="email_visibility", required=False)
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all(), required=True)

    class Meta:
        model = CompanyProfile
        fields = ('phoneVisibility', 'emailVisibility', 'telegramLink', 'vkLink',
                  'linkToCompany', 'description', 'skills')


class EmptySerializer2(serializers.Serializer):
    empty2 = serializers.CharField(required=False)


class leadTaskCategoriesSerializer(serializers.Serializer):
    id = serializers.UUIDField
    name = serializers.CharField
    percent = serializers.FloatField()


class GetCompanyProfileSerializer(BaseProfileSerializer):
    linkToCompany = serializers.URLField(source="link_to_company")
    companyName = serializers.CharField(source="company_name")
    city = CitySerializer()
    skills = SkillSerializer(many=True)
    leadTaskCategories = serializers.SerializerMethodField()

    class Meta(BaseProfileSerializer.Meta):
        model = CompanyProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('linkToCompany', 'companyName', 'skills', 'leadTaskCategories')

    @staticmethod
    def get_leadTaskCategories(obj) -> leadTaskCategoriesSerializer:
        queryset = TaskCategory.objects.annotate(
            solved_count=Count("tasks", filter=Q(
                tasks__user=obj.user,
            ))
        ).filter(solved_count__gt=0).order_by('-solved_count')

        total_solved = sum(i.solved_count for i in queryset)
        res = []
        for i in queryset:
            percent = round((i.solved_count / total_solved), 2)
            res.append(
                {
                    'id': str(i.id),
                    'name': i.name,
                    'percent': percent,
                }
            )
        return res




class GetStudentProfileSerializer(BaseProfileSerializer):
    formOfEducation = serializers.CharField(source="form_of_education")
    admissionYear = serializers.IntegerField(source="admission_year")
    university = UniversitySerializer()
    city = CitySerializer()
    faculty = FacultySerializer()
    skills = SkillSerializer(many=True)
    specialty = SpecialtySerializer()
    replyCount = serializers.SerializerMethodField()
    replyReloadDate = serializers.DateTimeField(source="reply_reload_date", read_only=True)
    leadTaskCategories = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta(BaseProfileSerializer.Meta):
        model = StudentProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('formOfEducation', 'admissionYear', 'university', 'faculty', 'skills',
                  'specialty', 'replyCount', 'replyReloadDate', 'profession', 'leadTaskCategories', "level")

    @staticmethod
    def get_level(obj):
        return {
            'value': obj.level_id,
            'name': obj.get_level_id_display(),
        }

    @staticmethod
    def get_leadTaskCategories(obj) -> leadTaskCategoriesSerializer:
        queryset = TaskCategory.objects.annotate(
            solved_count=Count("tasks__solutions", filter=Q(
                tasks__solutions__user=obj.user,
                tasks__solutions__status=Solution.COMPLETED,
            ))
        ).filter(solved_count__gt=0).order_by('-solved_count')

        total_solved = sum(i.solved_count for i in queryset[:2])
        res = []
        for i in queryset[:2]:
            percent = round((i.solved_count / total_solved), 2)
            res.append(
                {
                    'id': str(i.id),
                    'name': i.name,
                    'percent': percent,
                }
            )
        return res

    @staticmethod
    def get_replyCount(obj):
        return obj.get_reply_count()


class TestProfileVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    status = serializers.CharField()
    comment = serializers.CharField()


class ChangeStudentLogoImgSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(source="logo_img", required=True, allow_empty_file=False)

    class Meta:
        model = StudentProfile
        fields = ('logo',)


class ChangeCompanyLogoImgSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(source="logo_img", required=True, allow_empty_file=False)

    class Meta:
        model = CompanyProfile
        fields = ('logo',)
