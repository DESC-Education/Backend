from rest_framework import serializers

from Profiles.models import StudentProfile, CompanyProfile, BaseProfile


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


class CreateStudentProfileSerializer(BaseProfileSerializer):
    formOfEducation = serializers.CharField(source="form_of_education")
    admissionYear = serializers.IntegerField(source="admission_year")
    studentCard = serializers.ImageField(source="student_card")

    class Meta(BaseProfileSerializer.Meta):
        model = StudentProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('formOfEducation', 'university', 'speciality', 'admissionYear', 'studentCard')




class CreateCompanyProfileSerializer(BaseProfileSerializer):
    linkToCompany = serializers.URLField(source="link_to_company")
    companyName = serializers.CharField(source="company_name")

    class Meta(BaseProfileSerializer.Meta):
        model = CompanyProfile
        fields = BaseProfileSerializer.Meta.fields + \
                 ('linkToCompany', 'companyName')



class EmptySerializer(serializers.Serializer):
    empty = serializers.CharField()
