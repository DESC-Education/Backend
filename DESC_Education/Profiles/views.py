import logging
import random
import re
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from Profiles.permissions import IsCompanyOrStudentRole
from Settings.permissions import IsStudentRole
from rest_framework.response import Response
from django.shortcuts import render
from Profiles.utils.generate_profile_report import generate_pdf
from django.template.loader import render_to_string
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.utils.decorators import method_decorator
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
    StudentProfileSerializer,
    CreateCompanyProfileSerializer,
    EmptySerializer2,
    GetCompanyProfileSerializer,
    GetStudentProfileSerializer,
    UniversitySerializer,
    SkillSerializer,
    CitySerializer,
    SpecialtySerializer,
    FacultySerializer,
    ChangeCompanyLogoImgSerializer,
    ChangeStudentLogoImgSerializer,
    SendPhoneCodeSerializer,
    SetPhoneSerializer,
    EditStudentProfileSerializer,
    EditCompanyProfileSerializer,
    TestProfileVerifySerializer

)
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from Users.models import (
    CustomUser,
)
from Profiles.filters import (
    FacultiesFilter
)
from Files.models import (
    File
)
from Profiles.models import (
    BaseProfile,
    StudentProfile,
    CompanyProfile,
    ProfileVerifyRequest,
    University,
    Skill,
    City,
    Specialty,
    Faculty,
    PhoneVerificationCode
)
from rest_framework import filters


class ProfileView(generics.GenericAPIView):
    serializer_class = StudentProfileSerializer
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsCompanyOrStudentRole]
    profile_class = None
    profile_str_name = {
        StudentProfile: 'studentProfile',
        CompanyProfile: 'companyProfile',
    }

    serializer_classes = {
        CustomUser.COMPANY_ROLE: (CreateCompanyProfileSerializer, CompanyProfile),
        CustomUser.STUDENT_ROLE: (StudentProfileSerializer, StudentProfile)
    }

    get_serializer_classes = {
        CustomUser.COMPANY_ROLE: GetCompanyProfileSerializer,
        CustomUser.STUDENT_ROLE: GetStudentProfileSerializer
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
                    "specialty": 'uuid',
                    "admissionYear": "int",
                    "university": 'uuid',
                    "faculty": "uuid",
                    "city": "uuid",
                    'skills': ["uuid", "uuid"],
                    "files": [{"file": "file"}],
                    'profession': 'str'
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
                    "specialty": 'uuid',
                    "admissionYear": 'int',
                    "university": 'uuid',
                    "faculty": "uuid",
                    "city": "uuid",
                    'skills': ["uuid", "uuid"],
                    "files": [{"file": "file"}],
                    'profession': 'str'
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
                    "specialty": 'uuid',
                    "admissionYear": 'int',
                    "university": 'uuid',
                    "faculty": "uuid",
                    "city": "uuid",
                    'skills': ["uuid", "uuid"],
                    "files": [{"file": "file"}],
                    'profession': 'str'
                },
            ),
            OpenApiExample(
                "Компания",
                value={
                    "firstName": 'str',
                    "lastName": 'str',
                    "description": "str",
                    "phone": "str",
                    "phoneVisibility": True,
                    "emailVisibility": True,
                    "telegramLink": "https://t.me/example",
                    "vkLink": "https://vk.com/example",
                    "timezone": 7,
                    'linkToCompany': "https://link.com/example",
                    "companyName": "str",
                    "city": "uuid",
                    'skills': ["uuid", "uuid"],
                    "files": [
                        {
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
                            'admissionYear': 'int',
                            'description': 'str',
                            'emailVisibility': "bool",
                            'firstName': 'str',
                            'formOfEducation': 'str',
                            'id': 'uuid',
                            'isVerified': 'bool',
                            'lastName': 'str',
                            'logoImg': 'bool',
                            'phone': "str",
                            'phoneVisibility': 'bool',
                            'specialty': {
                                'id': 'uuid',
                                'name': 'str',
                                'type': 'str',
                                'code': 'str'
                            },
                            'telegramLink': 'str',
                            'timezone': 3,
                            'city': {
                                'id': 'uuid',
                                'name': 'str',
                                'region': 'str'},
                            'university': {
                                'id': 'uuid',
                                'name': 'str',
                                'city': {
                                    'id': 'uuid',
                                    'name': 'str',
                                    'region': 'str'}
                            },
                            "faculty": {
                                'id': 'uuid',
                                'name': 'str',
                                'university': 'uuid'
                            },
                            'vkLink': 'str',
                            'skills': [
                                {'id': 'uuid', 'name': 'str'},
                                {'id': 'uuid', 'name': 'str'}],
                            "replyCount": "int",
                            "replyReloadDate": "datetime",
                            'profession': 'str',
                            'leadTaskCategories': [
                                {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                            ],
                            'level': {
                                'value': 1,
                                'name': 'str',
                            }
                        }
                    ),
                    OpenApiExample(
                        "Компания Успешно",
                        value={
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
                            'vkLink': 'str',
                            'city': {
                                'id': 'uuid',
                                'name': 'str',
                                'region': 'str'},
                            'skills': [
                                {'id': 'uuid', 'name': 'str'},
                                {'id': 'uuid', 'name': 'str'}],
                            'leadTaskCategories': [
                                {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                            ]
                        }

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
            classes = self.serializer_classes.get(user.role)

            self.serializer_class = classes[0]
            self.profile_class = classes[1]

            profile: CompanyProfile = self.profile_class.objects.get(user=user)

            serializer = self.serializer_class(data=request.data, instance=profile)

            serializer.is_valid(raise_exception=True)

            if profile.verification == profile.VERIFIED:
                return Response({"message": "Профиль уже подтвержден"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            try:
                profile.verification_requests.get(status=ProfileVerifyRequest.PENDING)
                return Response({"message": "Профиль еще на проверке"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except ObjectDoesNotExist:
                pass

            profile = serializer.save()

            files_data = self.request.data.getlist('files')

            if profile.verification_files.count() != 0:
                profile.verification_files.all().delete()

            if len(files_data) == 0:
                return Response({"message": "Необходимо загрузить хотя бы одно изображение"},
                                status=status.HTTP_400_BAD_REQUEST)
            if len(files_data) > 6:
                files_data = files_data[:6]
            for file_data in files_data:
                File.objects.create(file=file_data,
                                    content_object=profile,
                                    type=File.VERIFICATION_FILE)

            ProfileVerifyRequest.objects.create(profile=profile)

            res_serializer = self.get_serializer_classes[user.role](profile)

            return Response(res_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logging.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetMyProfileView(generics.GenericAPIView):
    serializer_class = EmptySerializer2
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyOrStudentRole]
    profile_classes = {
        CustomUser.STUDENT_ROLE: StudentProfile,
        CustomUser.COMPANY_ROLE: CompanyProfile
    }

    profile_serializer_class = {
        CustomUser.STUDENT_ROLE: GetStudentProfileSerializer,
        CustomUser.COMPANY_ROLE: GetCompanyProfileSerializer
    }

    str_profile_classes = {
        CustomUser.STUDENT_ROLE: "studentProfile",
        CustomUser.COMPANY_ROLE: "companyProfile"
    }

    @extend_schema(
        tags=["Profiles"],
        summary="Получение своего профиля",
        description="Необходима авторизация",
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Студент Успешно",
                        value={
                            'admissionYear': 'int',
                            'description': 'str',
                            'emailVisibility': "bool",
                            'firstName': 'str',
                            'formOfEducation': 'str',
                            'id': 'uuid',
                            'isVerified': 'bool',
                            'lastName': 'str',
                            'logoImg': 'bool',
                            'phone': "str",
                            'phoneVisibility': 'bool',
                            'specialty': {
                                'id': 'uuid',
                                'name': 'str',
                                'type': 'str',
                                'code': 'str'
                            },
                            'telegramLink': 'str',
                            'timezone': 3,
                            'city': {
                                'id': 'uuid',
                                'name': 'str',
                                'region': 'str'},
                            'university': {
                                'id': 'uuid',
                                'name': 'str',
                                'city': {
                                    'id': 'uuid',
                                    'name': 'str',
                                    'region': 'str'}
                            },
                            "faculty": {
                                'id': 'uuid',
                                'name': 'str',
                                'university': 'uuid'
                            },
                            'vkLink': 'str',
                            'skills': [
                                {'id': 'uuid', 'name': 'str'},
                                {'id': 'uuid', 'name': 'str'},
                            ],
                            "replyCount": "int",
                            "replyReloadDate": "datetime",
                            'profession': 'str',
                            'leadTaskCategories': [
                                {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                            ],
                            'level': {
                                'value': 1,
                                'name': 'str',
                            }
                        }

                    ),
                    OpenApiExample(
                        "Компания Успешно",
                        value={

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
                            'vkLink': 'str',
                            'city': {
                                'id': 'uuid',
                                'name': 'str',
                                'region': 'str'},
                            'skills': [
                                {'id': 'uuid', 'name': 'str'},
                                {'id': 'uuid', 'name': 'str'}],
                            'leadTaskCategories': [
                                {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                            ]

                        }

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
            profile = user.get_profile()
            serializer = self.profile_serializer_class.get(user.role)
            if serializer is None:
                return Response('', status=status.HTTP_400_BAD_REQUEST)
            serializer = serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetProfileView(generics.GenericAPIView):
    serializer_class = EmptySerializer2
    permission_classes = [AllowAny]
    profile_classes = {
        CustomUser.STUDENT_ROLE: StudentProfile,
        CustomUser.COMPANY_ROLE: CompanyProfile
    }
    profile_serializer_class = {
        CustomUser.STUDENT_ROLE: GetStudentProfileSerializer,
        CustomUser.COMPANY_ROLE: GetCompanyProfileSerializer
    }

    str_profile_classes = {
        CustomUser.STUDENT_ROLE: "studentProfile",
        CustomUser.COMPANY_ROLE: "companyProfile"
    }

    @extend_schema(
        tags=["Profiles"],
        summary="Получение профиля пользователя по id user",
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Студент Успешно",
                        value={'admissionYear': 'int',
                               'description': 'str',
                               'firstName': 'str',
                               'formOfEducation': 'str',
                               'id': 'uuid',
                               'isVerified': 'bool',
                               'lastName': 'str',
                               'logoImg': 'bool',
                               "phone": "str",
                               'specialty': {
                                   'id': 'uuid',
                                   'name': 'str',
                                   'type': 'str',
                                   'code': 'str'
                               },
                               'telegramLink': 'str',
                               'timezone': 3,
                               'city': {
                                   'id': 'uuid',
                                   'name': 'str',
                                   'region': 'str'},
                               'university': {
                                   'id': 'uuid',
                                   'name': 'str',
                                   'city': {
                                       'id': 'uuid',
                                       'name': 'str',
                                       'region': 'str'}
                               },
                               "faculty": {
                                   'id': 'uuid',
                                   'name': 'str',
                                   'university': 'uuid'
                               },
                               'vkLink': 'str',
                               'skills': [
                                   {'id': 'uuid', 'name': 'str'},
                                   {'id': 'uuid', 'name': 'str'}],
                               'profession': 'str',
                               'leadTaskCategories': [
                                   {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                   {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                               ],
                               'level': {
                                   'value': 1,
                                   'name': 'str',
                               }
                               }

                    ),
                    OpenApiExample(
                        "Компания Успешно",
                        value={

                            'linkToCompany': "str",
                            "companyName": "str",
                            'description': 'str',
                            'firstName': 'str',
                            'id': 'uuid',
                            'isVerified': 'bool',
                            'lastName': 'str',
                            'logoImg': 'bool',
                            'phone': 'str',
                            'telegramLink': 'str',
                            'timezone': 3,
                            'vkLink': 'str',
                            'city': {
                                'id': 'uuid',
                                'name': 'str',
                                'region': 'str'},
                            'skills': [
                                {'id': 'uuid', 'name': 'str'},
                                {'id': 'uuid', 'name': 'str'}],
                            'leadTaskCategories': [
                                {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                            ]
                        }

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
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Профиль не найден",
                        value={
                            "message": "Профиль не найден"
                        },
                    )
                ]
            ),
        }

    )
    def get(self, request, pk):
        try:
            try:
                user = CustomUser.objects.get(id=pk)
                profile = self.profile_classes[user.role].objects.get(user=user, verification=BaseProfile.VERIFIED)
            except ObjectDoesNotExist:
                return Response({"message": "Профиль не найден"}, status=status.HTTP_404_NOT_FOUND)
            profile_data = self.profile_serializer_class[user.role](profile).data

            Phone_V = profile_data.pop('phoneVisibility')
            if not Phone_V:
                profile_data.pop('phone')
            Email_V = profile_data.pop('emailVisibility')
            if Email_V:
                profile_data['email'] = user.email

            profile_data.pop('replyCount', None)
            profile_data.pop("replyReloadDate", None)

            return Response(profile_data, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChangeLogoImgView(generics.GenericAPIView):
    serializer_class = ChangeStudentLogoImgSerializer
    permission_classes = [IsCompanyOrStudentRole]

    logo_serializer_class = {
        CustomUser.STUDENT_ROLE: ChangeStudentLogoImgSerializer,
        CustomUser.COMPANY_ROLE: ChangeCompanyLogoImgSerializer
    }

    profile_classes = {
        CustomUser.STUDENT_ROLE: StudentProfile,
        CustomUser.COMPANY_ROLE: CompanyProfile
    }

    @extend_schema(
        tags=["Profiles"],
        summary="Изменение изображения профиля",
        examples=[
            OpenApiExample(
                "Пример",
                value={
                    'logo': 'file'
                },
            )
        ],
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            'logo': 'urlpath'
                        },

                    ),
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
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Профиль не найден",
                        value={
                            "message": "Профиль не найден"
                        },
                    )
                ]
            ),
        }

    )
    def post(self, request):
        try:
            user = request.user
            serializer = self.logo_serializer_class[user.role](data=request.data, instance=user.get_profile(),
                                                               partial=True)
            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response({"logo": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendPhoneCodeView(generics.GenericAPIView):
    serializer_class = SendPhoneCodeSerializer
    permission_classes = [IsCompanyOrStudentRole]

    @extend_schema(
        tags=["Profiles"],
        summary="Отправить код подтверждения телефона",
        examples=[
            OpenApiExample(
                "Пример",
                value={
                    'phone': '+79999999999'
                },
            )
        ],
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "message": "Код подтверждения отправлен"}
                    ),
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
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Данный номер телефона уже привязан!",
                        value={
                            "message": "Данный номер телефона уже привязан!"
                        },
                    )
                ]
            ),

            406: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверный формат номера телефона",
                        value={
                            "message": "Неверный формат номера телефона"
                        },
                    )
                ]
            ),
            409: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Задержка между запросами",
                        value={
                            "message": "Код подтверждения уже был отправлен. Пожалуйста, повторите попытку позже."
                        },
                    )
                ]
            ),
        }

    )
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            phone = serializer.validated_data['phone']

            if not re.match("^\\+?[1-9][0-9]{7,14}$", phone):
                return Response({"message": "Неверный формат номера телефона"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            if PhoneVerificationCode.objects.filter(phone=phone, is_used=True).exists():
                return Response({"message": "Данный номер телефона уже привязан!"}, status=status.HTTP_404_NOT_FOUND)

            p = PhoneVerificationCode.objects.filter(phone=phone, user=request.user, is_used=False)
            if len(p) != 0:
                p = p.first()
                if (timezone.now() - p.created_at).total_seconds() < 55:
                    return Response({
                        "message": "Код подтверждения уже был отправлен. Пожалуйста, повторите попытку позже."},
                        status=status.HTTP_409_CONFLICT)

            PhoneVerificationCode.objects.create(phone=phone,
                                                 code=PhoneVerificationCode.create_code(),
                                                 user=request.user)

            return Response({
                "message": "Код подтверждения отправлен"}, status=status.HTTP_200_OK)


        except Exception as e:
            logging.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SetPhoneView(generics.GenericAPIView):
    serializer_class = SetPhoneSerializer
    permission_classes = [IsCompanyOrStudentRole]
    profile_classes = {
        CustomUser.STUDENT_ROLE: StudentProfile,
        CustomUser.COMPANY_ROLE: CompanyProfile
    }

    @extend_schema(
        tags=["Profiles"],
        summary="Подтверждение номера телефона",
        examples=[
            OpenApiExample(
                "Пример",
                value={
                    'phone': '+79999999999',
                    'code': 111111
                },
            )
        ],
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            'phone': "+79999999999"
                        }
                    ),
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
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Данный номер телефона уже привязан!",
                        value={
                            "message": "Неверный номер телефона или код"
                        },
                    )
                ]
            ),
        }

    )
    def post(self, request):
        try:
            user = request.user
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            profile = user.get_profile()

            try:
                phone_verification_code = PhoneVerificationCode.objects.get(phone=serializer.validated_data['phone'],
                                                                            is_used=False,
                                                                            user=user)
            except ObjectDoesNotExist:
                return Response({"message": "Неверный номер телефона или код"}, status=status.HTTP_404_NOT_FOUND)

            profile.phone = phone_verification_code.phone
            profile.save()

            return Response({'phone': profile.phone}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EditProfileView(generics.GenericAPIView):
    serializer_class = EditStudentProfileSerializer
    permission_classes = [IsCompanyOrStudentRole]
    edit_profile_serializers = {
        CustomUser.STUDENT_ROLE: EditStudentProfileSerializer,
        CustomUser.COMPANY_ROLE: EditCompanyProfileSerializer
    }
    get_profile_serializers = {
        CustomUser.STUDENT_ROLE: GetStudentProfileSerializer,
        CustomUser.COMPANY_ROLE: GetCompanyProfileSerializer
    }
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
        summary="Изменение данных профиля",
        examples=[
            OpenApiExample(
                "Пример Студент",
                value={
                    'description': 'str',
                    "phoneVisibility": True,
                    "emailVisibility": True,
                    "telegramLink": "https://tg.com",
                    "vkLink": "https://vk.com",
                    'skills': [
                        'uuid',
                        'uuid',
                    ],
                    'profession': 'str'
                },
            ),
            OpenApiExample(
                "Пример Компания",
                value={
                    "description": "str",
                    "phoneVisibility": True,
                    "emailVisibility": True,
                    "telegramLink": "https://tg.com",
                    "vkLink": "https://vk.com",
                    "linkToCompany": "https://linkTocompany.com",
                    'skills': [
                        'uuid',
                        'uuid',
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
                            'admissionYear': 'int',
                            'description': 'str',
                            'firstName': 'str',
                            'formOfEducation': 'str',
                            'id': 'uuid',
                            'isVerified': 'bool',
                            'lastName': 'str',
                            'logoImg': 'bool',
                            'specialty': {
                                'id': 'uuid',
                                'name': 'str',
                                'type': 'str',
                                'code': 'str'
                            },
                            'telegramLink': 'str',
                            'timezone': 3,
                            'city': {
                                'id': 'uuid',
                                'name': 'str',
                                'region': 'str'},
                            'university': {
                                'id': 'uuid',
                                'name': 'str',
                                'city': {
                                    'id': 'uuid',
                                    'name': 'str',
                                    'region': 'str'}
                            },
                            "faculty": {
                                'id': 'uuid',
                                'name': 'str',
                                'university': 'uuid'
                            },
                            'vkLink': 'str',
                            'skills': [
                                {'id': 'uuid', 'name': 'str'},
                                {'id': 'uuid', 'name': 'str'}],
                            "replyCount": "int",
                            "replyReloadDate": "datetime",
                            'profession': 'str',
                            'leadTaskCategories': [
                                {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                            ],
                            'level': {
                                'value': 1,
                                'name': 'str',
                            }
                        }

                    ),
                    OpenApiExample(
                        "Успешно Компания",
                        value={
                            'linkToCompany': "str",
                            "companyName": "str",
                            'description': 'str',
                            'firstName': 'str',
                            'id': 'uuid',
                            'isVerified': 'bool',
                            'lastName': 'str',
                            'logoImg': 'bool',
                            'phone': 'str',
                            'telegramLink': 'str',
                            'timezone': 3,
                            'vkLink': 'str',
                            'city': {
                                'id': 'uuid',
                                'name': 'str',
                                'region': 'str'},
                            'skills': [
                                {'id': 'uuid', 'name': 'str'},
                                {'id': 'uuid', 'name': 'str'}],
                            'leadTaskCategories': [
                                {'id': 'uuid', 'name': 'str', 'percent': 0.1},
                                {'id': 'uuid', 'name': 'str', 'percent': 0.2}
                            ]
                        }

                    ),
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
    def post(self, request):
        try:
            user = request.user
            profile = user.get_profile()

            serializer = self.edit_profile_serializers[user.role](data=request.data, instance=profile, partial=True)
            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response(self.get_profile_serializers[user.role](profile).data, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UniversitiesList(generics.ListAPIView):
    queryset = University.objects.all().select_related("city")
    serializer_class = UniversitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @extend_schema(
        tags=["Profiles"],
        summary="Получение экземпляров Университетов"
    )
    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SkillsList(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @extend_schema(
        tags=["Profiles"],
        summary="Получение экземпляров Навыков"
    )
    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CitiesList(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @extend_schema(
        tags=["Profiles"],
        summary="Получение экземпляров Городов"
    )
    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SpecialtiesList(generics.ListAPIView):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    @extend_schema(
        tags=["Profiles"],
        summary="Получение экземпляров Специальностей"
    )
    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FacultiesList(generics.ListAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_class = FacultiesFilter

    @extend_schema(
        tags=["Profiles"],
        summary="Получение экземпляров Факультетов"
    )
    @method_decorator(cache_page(60 * 60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)




class GenerateProfileReportView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # user = request.user
        # profile = user.get_profile()
        # profile_data = StudentProfileSerializer(profile).data

        context = {
            # '123': 100000
            'firstName': "Ярослав",
            'lastName': "Павленко"
        }

        generate_pdf(context)

        # from django.shortcuts import render
        # return render(request, 'Profiles/profile_report.html', context=context)


class TestVerifyView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = TestProfileVerifySerializer

    profile_classes = {
        CustomUser.STUDENT_ROLE: StudentProfile,
        CustomUser.COMPANY_ROLE: CompanyProfile,
    }

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.get(email=serializer.validated_data['email'])
        profile = user.get_profile()
        v_request: ProfileVerifyRequest = profile.verification_requests.first()
        v_request.status = serializer.validated_data['status']
        v_request.comment = serializer.validated_data['comment']
        v_request.save()

        return Response(status=status.HTTP_200_OK)
