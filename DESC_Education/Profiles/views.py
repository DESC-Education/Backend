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

)
from Users.models import (
    CustomUser,
)

from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    ProfileVerifyRequest
)


class CreateStudentProfileView(generics.GenericAPIView):
    serializer_class = CreateStudentProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Profiles"],
        summary="Создание профиля студента",
        examples=[
            OpenApiExample(
                "Очное",
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
                "Заочное",
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
                "Очно-Заочное",
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


        ],
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
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
                                                   'phone': 'str',
                                                   'phoneVisibility': 'bool',
                                                   'speciality': 'str',
                                                   'studentCard': 'url',
                                                   'telegramLink': 'str',
                                                   'timezone': 3,
                                                   'university': 'uuid',
                                                   'vkLink': 'str'}
                            },
                            "message": "Профиль студента создан и отправлен на проверку!"}
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
                            "message": "Вы можете создать профиль студента только для студента!"
                        },
                    )
                ]
            ),
            409: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Профиль уже создан",
                        value={
                            "message": "Профиль с такими данными уже существует!"
                        },
                    )
                ]
            ),

        }

    )
    def post(self, request):
        try:
            if request.user.role != CustomUser.STUDENT_ROLE:
                return Response({"message": "Вы можете создать профиль студента только для студента!"},
                                status=status.HTTP_403_FORBIDDEN)

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["user"] = request.user

            try:
                profile: StudentProfile = StudentProfile.objects.create(**serializer.validated_data)
            except:
                return Response({"message": "Профиль с такими данными уже существует!"},
                                status=status.HTTP_409_CONFLICT)

            ProfileVerifyRequest.objects.create(
                object_id=profile.id, content_type=ContentType.objects.get_for_model(profile))

            resp = CreateStudentProfileSerializer(profile)
            return Response({
                "data": {
                    "studentProfile": resp.data
                },
                "message": "Профиль студента создан и отправлен на проверку!"})

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


