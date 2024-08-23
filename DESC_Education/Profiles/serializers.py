import random

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


class ChangeLogoImgSerializer(serializers.Serializer):
    logo = serializers.ImageField(required=True, allow_empty_file=False)


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


class BaseProfileSerializer(serializers.ModelSerializer):
    phoneVisibility = serializers.BooleanField(source="phone_visibility", required=True)
    emailVisibility = serializers.BooleanField(source="email_visibility", required=True)
    phone = serializers.CharField(read_only=True)
    firstName = serializers.CharField(source="first_name", required=True)
    lastName = serializers.CharField(source="last_name", required=True)
    telegramLink = serializers.URLField(source="telegram_link", required=False)
    vkLink = serializers.URLField(source="vk_link", required=False)
    logoImg = serializers.ImageField(source="logo_img", read_only=True)
    isVerified = serializers.BooleanField(source="is_verified", read_only=True)

    class Meta:
        model = BaseProfile
        fields = ('id', 'firstName', 'lastName', 'description', 'phone', 'phoneVisibility', 'emailVisibility',
                  'logoImg', 'telegramLink', 'vkLink', 'timezone', 'isVerified', 'city',)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name',)


class CreateStudentProfileSerializer(BaseProfileSerializer):
    formOfEducation = serializers.CharField(source="form_of_education", required=True)
    admissionYear = serializers.IntegerField(source="admission_year", required=True)
    skills_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True,
                                                    queryset=Skill.objects.all(),
                                                    source="skills")
    university = serializers.PrimaryKeyRelatedField(queryset=University.objects.all(), required=True)
    faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all(), required=True)
    specialty = serializers.PrimaryKeyRelatedField(queryset=Specialty.objects.all(), required=True)

    class Meta(BaseProfileSerializer.Meta):
        model = StudentProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('formOfEducation', 'university', 'faculty', 'admissionYear', 'skills_ids',
                  'specialty')



class EditStudentProfileSerializer(BaseProfileSerializer):
    phoneVisibility = serializers.BooleanField(source="phone_visibility", required=False)
    emailVisibility = serializers.BooleanField(source="email_visibility", required=False)

    class Meta:
        model = StudentProfile
        fields = ('phoneVisibility', 'emailVisibility', 'telegramLink', 'vkLink', )



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

    class Meta:
        model = CompanyProfile
        fields = ('phoneVisibility', 'emailVisibility', 'telegramLink', 'vkLink',
                  'linkToCompany',)



class EmptySerializer(serializers.Serializer):
    empty = serializers.CharField(required=False)


class GetCompanyProfileSerializer(BaseProfileSerializer):
    linkToCompany = serializers.URLField(source="link_to_company")
    companyName = serializers.CharField(source="company_name")
    city = CitySerializer()

    class Meta(BaseProfileSerializer.Meta):
        model = CompanyProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('linkToCompany', 'companyName',)


class GetStudentProfileSerializer(BaseProfileSerializer):
    formOfEducation = serializers.CharField(source="get_form_of_education_display")
    admissionYear = serializers.IntegerField(source="admission_year")
    university = UniversitySerializer()
    city = CitySerializer()
    faculty = FacultySerializer()
    skills = SkillSerializer(many=True)
    specialty = SpecialtySerializer()

    # skills = serializers.SerializerMethodField()

    class Meta(BaseProfileSerializer.Meta):
        model = StudentProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('formOfEducation', 'admissionYear', 'university', 'faculty', 'skills',
                  'specialty',)

    # def get_skills(self, obj):
    #     return [SkillSerializer(skill) for skill in obj.skills.filter(is_verified=True)]
