import random
from rest_framework.parsers import MultiPartParser
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    OpenApiRequest,
    inline_serializer)
from drf_spectacular.types import OpenApiTypes
from Profiles.serializers import (
    CreateStudentProfileSerializer,
    CreateCompanyProfileSerializer,
    EmptySerializer
)
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from Users.models import (
    CustomUser,
)

from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    ProfileVerifyRequest,
    File
)



class testView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    authentication_classes = [JWTAuthentication]
    # parser_classes = (MultiPartParser,)
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            files_data = self.request.data.getlist('files')
            profile = StudentProfile.objects.first()
            if profile.verification_files.count() != 0:
                profile.verification_files.all().delete()

            if len(files_data) == 0:
                return Response({"message": "Необходимо загрузить хотя бы одно изображение"},
                                status=status.HTTP_400_BAD_REQUEST)
            if len(files_data) > 6:
                files_data = files_data[:6]
            for file_data in files_data:
                File.objects.create(file=file_data, profile=profile)

            ProfileVerifyRequest.objects.create(profile=profile)

            return Response({
                "data": {
                    ''
                },
                "message": "Профиль создан и отправлен на проверку!"})

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ProfileView(generics.GenericAPIView):
    serializer_class = CreateStudentProfileSerializer
    authentication_classes = [JWTAuthentication]
    # parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated]
    profile_class = None
    profile_str_name = {
        StudentProfile: 'studentProfile',
        CompanyProfile: 'companyProfile',
    }

    serializer_classes = {
        CustomUser.COMPANY_ROLE: (CreateCompanyProfileSerializer, CompanyProfile),
        CustomUser.STUDENT_ROLE: (CreateStudentProfileSerializer, StudentProfile)
    }

    @extend_schema(
        tags=["Profiles"],
        summary="Создание профиля",
        examples=[
            OpenApiExample(
                "Студент(Очное)",
                value={
                    "firstName": 'str',
                    "lastName": 'str',
                    "description": "str",
                    "phone": "+79991234567",
                    "phoneVisibility": True,
                    "emailVisibility": True,
                    "telegramLink": "https://t.me/example",
                    "vkLink": "https://vk.com/example",
                    "timezone": 7,
                    "formOfEducation": StudentProfile.FULL_TIME_EDUCATION,
                    "speciality": 'str',
                    "admissionYear": 'str',
                    "university": 'uuid',
                    "files": [{"file": "file"}]
                },
            ),
            OpenApiExample(
                "Студент(Заочное)",
                value={
                    "firstName": 'str',
                    "lastName": 'str',
                    "description": "str",
                    "phone": "+79991234567",
                    "phoneVisibility": True,
                    "emailVisibility": True,
                    "telegramLink": "https://t.me/example",
                    "vkLink": "https://vk.com/example",
                    "timezone": 7,
                    "formOfEducation": StudentProfile.PART_TIME_EDUCATION,
                    "speciality": 'str',
                    "admissionYear": 'str',
                    "university": 'uuid',
                    "files": [{"file": "file"}]
                },
            ),
            OpenApiExample(
                "Студент(Очно-Заочное)",
                value={
                    "firstName": 'str',
                    "lastName": 'str',
                    "description": "str",
                    "phone": "+79991234567",
                    "phoneVisibility": True,
                    "emailVisibility": True,
                    "telegramLink": "https://t.me/example",
                    "vkLink": "https://vk.com/example",
                    "timezone": 7,
                    "formOfEducation": StudentProfile.FULL_TIME_AND_PART_TIME_EDUCATION,
                    "speciality": 'str',
                    "admissionYear": 'str',
                    "university": 'uuid',
                    "files": [{"file": "file"}]
                },
            ),
            OpenApiExample(
                "Компания",
                value={
                    "firstName": 'str',
                    "lastName": 'str',
                    "description": "str",
                    "phoneVisibility": True,
                    "emailVisibility": True,
                    "telegramLink": "https://t.me/example",
                    "vkLink": "https://vk.com/example",
                    "timezone": 7,
                    'linkToCompany': "https://link.com/example",
                    "companyName": "str",
                    "files": [{
                        "file": "file"
                    },
                        {
                            "file": "file"
                        },

                    ]
                },
            )

        ],
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Студент Успешно",
                        value={
                            "data": {
                                "studentProfile": {'admissionYear': 'int',
                                                   'description': 'str',
                                                   'emailVisibility': "bool",
                                                   'firstName': 'str',
                                                   'formOfEducation': 'str',
                                                   'id': 'uuid',
                                                   'isVerified': 'bool',
                                                   'lastName': 'str',
                                                   'logoImg': 'bool',
                                                   'phoneVisibility': 'bool',
                                                   'speciality': 'str',
                                                   'studentCard': 'url',
                                                   'telegramLink': 'str',
                                                   'timezone': 3,
                                                   'university': 'uuid',
                                                   'vkLink': 'str'}
                            },
                            "message": "Профиль студента создан и отправлен на проверку!"}
                    ),
                    OpenApiExample(
                        "Компания Успешно",
                        value={
                            "data": {
                                "companyProfile": {
                                    'linkToCompany': "str",
                                    "companyName": "str",
                                    'description': 'str',
                                    'emailVisibility': "bool",
                                    'firstName': 'str',
                                    'id': 'uuid',
                                    'isVerified': 'bool',
                                    'lastName': 'str',
                                    'logoImg': 'bool',
                                    'phone': 'str',
                                    'phoneVisibility': 'bool',
                                    'telegramLink': 'str',
                                    'timezone': 3,
                                    'vkLink': 'str'}
                            },
                            "message": "Профиль компании создан и отправлен на проверку!"}
                    )
                ]
            ),
            400: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Прочие ошибки",
                        value={
                            "message": "Сообщение об ошибке"
                        },
                    )
                ]
            ),
            401: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Не авторизован",
                        value={
                            "detail": "Учетные данные не были предоставлены."
                        },
                    )
                ]
            ),
            403: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверная роль",
                        value={
                            "message": "Вы можете создать профиль только для студента или компании!"
                        },
                    )
                ]
            ),
            405: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Профиль подтвержден",
                        value={
                            "message": "Профиль уже подтвержден"
                        },
                    ),
                    OpenApiExample(
                        "Профиль еще на проверке",
                        value={
                            "message": "Профиль еще на проверке"
                        },
                    )
                ]
            ),

        }

    )
    def post(self, request):
        try:


            user = request.user
            classes = self.serializer_classes.get(user.role, None)
            if classes is None:
                return Response({"message": "Вы можете создать профиль только для студента или компании!"},
                                status=status.HTTP_403_FORBIDDEN)

            self.serializer_class = classes[0]
            self.profile_class = classes[1]

            profile: CompanyProfile = self.profile_class.objects.get(user=user)

            serializer = self.serializer_class(data=request.data, instance=profile)

            serializer.is_valid(raise_exception=True)

            if profile.is_verified:
                return Response({"message": "Профиль уже подтвержден"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            try:
                profile.verification_requests.get(status=ProfileVerifyRequest.PENDING)
                return Response({"message": "Профиль еще на проверке"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except ObjectDoesNotExist:
                pass

            serializer.save()



            files_data = self.request.data.getlist('files')

            if profile.verification_files.count() != 0:
                profile.verification_files.all().delete()



            if len(files_data) == 0:
                return Response({"message": "Необходимо загрузить хотя бы одно изображение"}, status=status.HTTP_400_BAD_REQUEST)
            if len(files_data) > 6:
                files_data = files_data[:6]
            for file_data in files_data:
                File.objects.create(file=file_data, profile=profile)

            ProfileVerifyRequest.objects.create(profile=profile)




            return Response({
                "data": {
                   self.profile_str_name[self.profile_class]: serializer.data
                },
                "message": "Профиль создан и отправлен на проверку!"})

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class GetMyProfileView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    profile_classes = {
        CustomUser.STUDENT_ROLE: StudentProfile,
        CustomUser.COMPANY_ROLE: CompanyProfile
    }

    str_profile_classes = {
        CustomUser.STUDENT_ROLE: "studentProfile",
        CustomUser.COMPANY_ROLE: "companyProfile"
    }

    @extend_schema(
        tags=["Profiles"],
        summary="получение профиля",
        description="Необходима авторизация",
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Студент Успешно",
                        value={
                            "data": {
                                "studentProfile": {'admissionYear': 'int',
                                                   'description': 'str',
                                                   'emailVisibility': "bool",
                                                   'firstName': 'str',
                                                   'formOfEducation': 'str',
                                                   'id': 'uuid',
                                                   'isVerified': 'bool',
                                                   'lastName': 'str',
                                                   'logoImg': 'bool',
                                                   'phoneVisibility': 'bool',
                                                   'speciality': 'str',
                                                   'studentCard': 'url',
                                                   'telegramLink': 'str',
                                                   'timezone': 3,
                                                   'university': 'uuid',
                                                   'vkLink': 'str'}
                            },
                            "message": "Успешно!"}
                    ),
                    OpenApiExample(
                        "Компания Успешно",
                        value={
                            "data": {
                                "companyProfile": {
                                    'linkToCompany': "str",
                                    "companyName": "str",
                                    'description': 'str',
                                    'emailVisibility': "bool",
                                    'firstName': 'str',
                                    'id': 'uuid',
                                    'isVerified': 'bool',
                                    'lastName': 'str',
                                    'logoImg': 'bool',
                                    'phone': 'str',
                                    'phoneVisibility': 'bool',
                                    'telegramLink': 'str',
                                    'timezone': 3,
                                    'vkLink': 'str'}
                            },
                            "message": "Успешно!"}
                    )
                ]
            ),
            400: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Прочие ошибки",
                        value={
                            "message": "Сообщение об ошибке"
                        },
                    )
                ]
            ),
            401: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Не авторизован",
                        value={
                            "detail": "Учетные данные не были предоставлены."
                        },
                    )
                ]
            ),


        }

    )
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            profile = self.profile_classes[user.role].objects.get(user=user)
            serializer = CreateStudentProfileSerializer(profile)
            return Response({"data": {self.str_profile_classes[user.role] : serializer.data, "message": "Успешно!"}},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetProfileView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [AllowAny]
    profile_classes = {
        CustomUser.STUDENT_ROLE: StudentProfile,
        CustomUser.COMPANY_ROLE: CompanyProfile
    }

    str_profile_classes = {
        CustomUser.STUDENT_ROLE: "studentProfile",
        CustomUser.COMPANY_ROLE: "companyProfile"
    }

    def get(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
            print(user)
            print(123)


            return Response({"message": str(user)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)





