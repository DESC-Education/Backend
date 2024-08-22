from rest_framework import serializers

from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    BaseProfile,
    File,
    Skill,
    University,
    Faculty,
    City
)


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


class BaseProfileSerializer(serializers.ModelSerializer):
    phoneVisibility = serializers.BooleanField(source="phone_visibility")
    emailVisibility = serializers.BooleanField(source="email_visibility")
    phone = serializers.CharField(read_only=True)
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    telegramLink = serializers.URLField(source="telegram_link", required=False)
    vkLink = serializers.URLField(source="vk_link", required=False)
    logoImg = serializers.ImageField(source="logo_img", read_only=True)
    isVerified = serializers.BooleanField(source="is_verified", read_only=True)

    class Meta:
        model = BaseProfile
        fields = ('id', 'firstName', 'lastName', 'description', 'phone', 'phoneVisibility', 'emailVisibility',
                  'logoImg', 'telegramLink', 'vkLink', 'timezone', 'isVerified')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name',)


class CreateStudentProfileSerializer(BaseProfileSerializer):
    formOfEducation = serializers.CharField(source="form_of_education")
    educationProgram = serializers.CharField(source="education_program")
    admissionYear = serializers.IntegerField(source="admission_year")
    skills_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True,
                                                    queryset=Skill.objects.all(),
                                                    source="skills")

    class Meta(BaseProfileSerializer.Meta):
        model = StudentProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('formOfEducation', 'university', 'speciality', 'admissionYear', 'skills_ids',
                  'educationProgram')


class CreateCompanyProfileSerializer(BaseProfileSerializer):
    linkToCompany = serializers.URLField(source="link_to_company")
    companyName = serializers.CharField(source="company_name")

    class Meta(BaseProfileSerializer.Meta):
        model = CompanyProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('linkToCompany', 'companyName',)


class EmptySerializer(serializers.Serializer):
    empty = serializers.CharField(required=False)


class GetCompanyProfileSerializer(BaseProfileSerializer):
    linkToCompany = serializers.URLField(source="link_to_company")
    companyName = serializers.CharField(source="company_name")

    class Meta(BaseProfileSerializer.Meta):
        model = CompanyProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('linkToCompany', 'companyName',)


class GetStudentProfileSerializer(BaseProfileSerializer):
    formOfEducation = serializers.CharField(source="get_form_of_education_display")
    educationProgram = serializers.CharField(source="get_education_program_display")
    admissionYear = serializers.IntegerField(source="admission_year")
    university = UniversitySerializer()
    skills = SkillSerializer(many=True)


    # skills = serializers.SerializerMethodField()

    class Meta(BaseProfileSerializer.Meta):
        model = StudentProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('formOfEducation', 'admissionYear', 'university', 'speciality', 'skills',
                  'educationProgram')

    # def get_skills(self, obj):
    #     return [SkillSerializer(skill) for skill in obj.skills.filter(is_verified=True)]
