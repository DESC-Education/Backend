import random

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
)
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from Users.models import (
    CustomUser,
)

from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    ProfileVerifyRequest
)


class CreateProfileView(generics.GenericAPIView):
    serializer_class = CreateStudentProfileSerializer
    authentication_classes = [JWTAuthentication]
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
                    "studentCard": 'image'
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
                    "studentCard": 'image'
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
                    "studentCard": 'image'
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

            ProfileVerifyRequest.objects.create(
                object_id=profile.id, content_type=ContentType.objects.get_for_model(profile))


            return Response({
                "data": {
                   self.profile_str_name[self.profile_class]: serializer.data
                },
                "message": "Профиль создан и отправлен на проверку!"})

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



