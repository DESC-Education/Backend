import random

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from Settings.permissions import IsAuthenticatedAndVerified
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import time
from Mail import tasks
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import logging
from django.utils import timezone
from Users.models import (
    CustomUser,
    VerificationCode,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    OpenApiRequest,
    inline_serializer)
from drf_spectacular.types import OpenApiTypes
from Users.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    VerifyRegistrationSerializer,
    CustomUserSerializer,
    EmptySerializer,
    VerifyCodeSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    TestDeleteSerializer
)
from Users.smtp import (
    send_auth_registration_code,
    send_password_change_code,
    send_mail_change_code
)
from Notifications.models import Notification
from Notifications.serializers import NotificationSerializer


# Create your views here.


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Users"],
        summary="Авторизация пользователя",
        # examples=[OpenApiExample(
        #     "123",
        #     value=[
        #         {'title': 'A title'},
        #         {'title': 'Another title'},
        #     ],
        # )],
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "user": {
                                "id": "uuid",
                                "email": "str",
                                "role": "str",
                                "isActive": "bool",
                                "isStaff": "bool",
                                "isSuperuser": "bool"
                            }
                            ,
                            "tokens": {
                                "accessToken": "str",
                                "refreshToken": "str"
                            }
                        }
                    )
                ]
            ),
            401: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверные данные",
                        value={
                            "message": "Неверный адрес электронной почты или пароль"
                        },
                    )
                ]
            ),
            406: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Почта не подтверждена",
                        value={
                            "message": "Вам нужно подтвердить адрес электронной почты"
                        },
                    )
                ]
            ),
            400: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Прочие ошибки",
                        value={
                            "message": "Другое сообщение об ошибке"
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

            email = serializer.validated_data['email']

            try:
                user: CustomUser = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({'message': 'Неверный адрес электронной почты или пароль'},
                                status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(serializer.validated_data['password']):
                return Response({'message': 'Неверный адрес электронной почты или пароль'},
                                status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_verified:
                return Response({'message': 'Вам нужно подтвердить адрес электронной почты'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            tokens = user.get_token()

            user_serializer = CustomUserSerializer(user)
            return Response({
                "user": user_serializer.data,
                "tokens": tokens
            },
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"},
                            status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Users"],
        summary="Регистрация пользователя",
        examples=[
            OpenApiExample(
                "Регистрация студента",
                description='Дефолтный вариант, можно не указывать role',
                value={
                    "email": "user@example.com",
                    "password": "string",
                    "role": "student"
                },
            ),
            OpenApiExample(
                "Регистрация компании",
                value={
                    "email": "user@example.com",
                    "password": "string",
                    "role": "company"
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
                            "message": "Код подтверждения отправлен на электронную почту"
                        },
                    )
                ]
            ),
            406: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Почта занята",
                        value={
                            "message": "Адрес электронной почты уже зарегистрирован"
                        },
                    )
                ]
            ),
            400: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Прочие ошибки",
                        value={
                            "message": "Другое сообщение об ошибке"
                        },
                    )
                ]
            ),
        }

    )
    def post(self, request):
        try:
            start_time = time.time()
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            role = serializer.validated_data['role']

            if CustomUser.objects.filter(email=email).exists():
                return Response(
                    {'message': 'Адрес электронной почты уже зарегистрирован'},
                    status=status.HTTP_406_NOT_ACCEPTABLE)

            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                role=role
            )

            Vcode: VerificationCode = VerificationCode.objects.create(
                user=user,
                code=random.randint(1000, 9999),
                type=VerificationCode.REGISTRATION_TYPE
            )

            tasks.MailVerifyRegistration.delay(email, Vcode.code)
            # send_auth_registration_code(email, Vcode.code)

            return Response({"message": "Код подтверждения отправлен на электронную почту"},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"},
                            status=status.HTTP_400_BAD_REQUEST)


class VerifyRegistrationView(generics.GenericAPIView):
    serializer_class = VerifyRegistrationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Users"],
        summary="Подтверждение регистрации",
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "user": {
                                "id": "uuid",
                                "email": "str",
                                "role": "str",
                                "isActive": "bool",
                                "isStaff": "bool",
                                "isSuperuser": "bool"
                            }
                            ,
                            "tokens": {
                                "accessToken": "str",
                                "refreshToken": "str"
                            }
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Код истек",
                        value={
                            "message": "Срок действия проверочного кода истек, запросите новый"
                        },
                    )
                ]
            ),
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Пользователь не найден",
                        value={
                            "message": "Пользователь не найден"
                        },
                    )
                ]
            ),
            406: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверный код",
                        value={
                            "message": "Проверочный код не существует или не соответствует"
                        },
                    )
                ]
            ),
            400: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Прочие ошибки",
                        value={
                            "message": "Другое сообщение об ошибке"
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

            code = serializer.validated_data['code']
            email = serializer.validated_data['email']

            try:
                user: CustomUser = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"message": "Пользователь не найден"},
                                status=status.HTTP_404_NOT_FOUND)

            Vcode: VerificationCode = VerificationCode.objects.filter(user=user,
                                                                      type=VerificationCode.REGISTRATION_TYPE,
                                                                      is_used=False)
            if len(Vcode) == 0:
                return Response({"message": "Проверочный код не существует или не соответствует"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            Vcode = Vcode.first()

            if Vcode.code != code:
                return Response({"message": "Проверочный код не существует или не соответствует"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            if not Vcode.is_valid():
                return Response({"message": "Срок действия проверочного кода истек, запросите новый"},
                                status=status.HTTP_403_FORBIDDEN)

            user.is_verified = True
            user.save()
            Vcode.is_used = True
            Vcode.save()

            tokens = user.get_token()

            user_serializer = CustomUserSerializer(user)

            return Response({
                "user": user_serializer.data,
                "tokens": tokens
            }, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        tags=["Users"],
        summary="Обновление access токена",
        responses={
            200: OpenApiResponse(
                EmptySerializer,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "access": "str"
                        },
                    )
                ]
            ),
            401: OpenApiResponse(
                EmptySerializer,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "detail": "Токен недействителен или просрочен"
                        },
                    )
                ]
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AuthView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    @extend_schema(
        tags=["Users"],
        summary="Получение user",
        examples=None,
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "id": "uuid",
                            "email": "str",
                            "role": "str",
                            "isActive": "bool",
                            "isStaff": "bool",
                            "isSuperuser": "bool"
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
                            "message": "Другое сообщение об ошибке"
                        },
                    )
                ]
            ),
            401: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Ошибка",
                        value={
                            "detail": "Учетные данные не были предоставлены."
                        },
                    )
                ]
            ),

        }

    )

    def get(self, request):
        try:
            user = request.user
            serializer = CustomUserSerializer(user)

            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class SendVerifyCodeView(generics.GenericAPIView):
    serializer_class = VerifyCodeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Users"],
        summary="Отправка кода подтверждения",
        examples=[
            OpenApiExample(
                "Подтверждение регистрации",
                description='НЕ ТРЕБУЕТСЯ аторизация!',
                value={
                    "type": "RG",
                    "email": "user@example.com"
                },
            ),
            OpenApiExample(
                "Подтверждение смены пароля",
                description='НЕ ТРЕБУЕТСЯ аторизация!\n',
                value={
                    "type": "PW",
                    "email": "user@example.com"
                },
            ),
            OpenApiExample(
                "Подтверждение смены почты",
                description='ТРЕБУЕТСЯ аторизация!\n'
                            'Необходимо указывать новую почту.\n'
                            'Код подтверждения будет отправлен на новую почту',
                value={
                    "type": "EM",
                    "email": "user@example.com"
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
                            "message": "Код подтверждения отправлен на электронную почту"
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
                            "message": "Другое сообщение об ошибке"
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
                            "message": "Пользователь не авторизован"
                        },
                    )
                ]
            ),
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Пользователь не существует",
                        value={
                            "message": "Пользователь не найден"
                        },
                    )
                ]
            ),
            405: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Пользователь уже верифицирован",
                        value={
                            "message": "Пользователь уже верифицирован"
                        },
                    )
                ]
            ),
            406: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверный тип кода",
                        value={
                            "message": "Неверный тип кода"
                        },
                    )
                ]
            ),
            409: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Слишком часто",
                        value={
                            "message": "Проверочный код по-прежнему активен, повторите попытку позже"
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

            type = serializer.validated_data['type']

            match type:
                case self.serializer_class.REGISTRATION_TYPE:
                    email = serializer.validated_data['email']
                    try:
                        user = CustomUser.objects.get(email=email)

                        if user.is_verified:
                            return Response({"message": "Пользователь уже верифицирован"},
                                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

                    except CustomUser.DoesNotExist:
                        return Response({"message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

                    Vcode: VerificationCode = VerificationCode.objects.filter(user=user,
                                                                              type=VerificationCode.REGISTRATION_TYPE,
                                                                              is_used=False)
                    if len(Vcode) != 0:
                        code = Vcode.first()

                        if code.get_time() < 55:
                            return Response({"message": "Проверочный код по-прежнему активен, повторите попытку позже"},
                                            status=status.HTTP_409_CONFLICT)

                    Vcode_reg = VerificationCode.objects.create(user=user,
                                                                code=str(random.randint(1000, 9999)),
                                                                type=VerificationCode.REGISTRATION_TYPE)

                    send_auth_registration_code(email, Vcode_reg.code)

                    return Response({"message": "Код подтверждения отправлен на электронную почту"},
                                    status=status.HTTP_200_OK)

                case self.serializer_class.EMAIL_CHANGE_TYPE:
                    email = serializer.validated_data['email']

                    if not request.user.is_authenticated:
                        return Response({"message": "Пользователь не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)

                    Vcode: VerificationCode = VerificationCode.objects.filter(user=request.user,
                                                                              type=VerificationCode.EMAIL_CHANGE_TYPE,
                                                                              is_used=False)
                    if len(Vcode) != 0:
                        code = Vcode.first()
                        if code.get_time() < 55:
                            return Response({"message": "Проверочный код по-прежнему активен, повторите попытку позже"},
                                            status=status.HTTP_409_CONFLICT)

                    Vcode_email = VerificationCode.objects.create(user=request.user,
                                                                  code=str(random.randint(1000, 9999)),
                                                                  type=VerificationCode.EMAIL_CHANGE_TYPE,
                                                                  new_email=email)
                    send_mail_change_code(email, Vcode_email.code)

                    return Response({"message": "Код подтверждения отправлен на электронную почту"},
                                    status=status.HTTP_200_OK)

                case self.serializer_class.PASSWORD_CHANGE_TYPE:
                    email = serializer.validated_data['email']
                    try:
                        user = CustomUser.objects.get(email=email)

                        if not user.is_verified:
                            return Response({"message": "User not verified"},
                                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

                    except CustomUser.DoesNotExist:
                        return Response({"message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

                    Vcode: VerificationCode = VerificationCode.objects.filter(user=user,
                                                                              type=VerificationCode.PASSWORD_CHANGE_TYPE,
                                                                              is_used=False)
                    if len(Vcode) != 0:
                        code = Vcode.first()
                        if code.get_time() < 55:
                            return Response({"message": "Проверочный код по-прежнему активен, повторите попытку позже"},
                                            status=status.HTTP_409_CONFLICT)

                    Vcode_pass = VerificationCode.objects.create(user=user,
                                                                 code=random.randint(1000, 9999),
                                                                 type=VerificationCode.PASSWORD_CHANGE_TYPE)

                    send_password_change_code(user.email, Vcode_pass.code)

                    return Response({"message": "Код подтверждения отправлен на электронную почту"},
                                    status=status.HTTP_200_OK)

                case _:
                    return Response({"message": "Неверный тип кода"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Users"],
        summary="Смена пароля",
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "message": "Пароль был изменен"
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
                            "message": "Другое сообщение об ошибке"
                        },
                    )
                ]
            ),
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Код не найден или истек",
                        value={
                            "message": "Проверочный код не найден или срок действия истек"
                        },
                    )
                ]
            ),
            406: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверный код",
                        value={
                            "message": "Неверный проверочный код"
                        },
                    )
                ]
            ),
            409: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Пользователь не найден",
                        value={
                            "message": "Пользователь не найден"
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

            email = serializer.validated_data["email"]

            try:
                user: CustomUser = CustomUser.objects.get(email=email)

            except CustomUser.DoesNotExist:
                return Response({"message": "Пользователь не найден"}, status=status.HTTP_409_CONFLICT)

            Vcode = VerificationCode.objects.filter(user=user,
                                                    type=VerificationCode.PASSWORD_CHANGE_TYPE,
                                                    is_used=False)
            if len(Vcode) == 0:
                return Response({"message": "Проверочный код не найден или срок действия истек"},
                                status=status.HTTP_404_NOT_FOUND)
            Vcode = Vcode.first()
            #
            if not Vcode.is_valid():
                return Response({"message": "Проверочный код не найден или срок действия истек"},
                                status=status.HTTP_404_NOT_FOUND)
            #
            if Vcode.code != serializer.validated_data["code"]:
                return Response({"message": "Неверный проверочный код"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"message": "Пароль был изменен"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(generics.GenericAPIView):
    serializer_class = ChangeEmailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedAndVerified]

    @extend_schema(
        tags=["Users"],
        summary="Смена почты",
        responses={
            200: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Успешно",
                        value={
                            "message": "Адрес электронной почты был изменен"
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
                            "message": "Другое сообщение об ошибке"
                        },
                    )
                ]
            ),
            404: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Код не найден или истек",
                        value={
                            "message": "Проверочный код не найден или срок действия истек"
                        },
                    )
                ]
            ),
            406: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверный код",
                        value={
                            "message": "Неверный проверочный код"
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

            Vcode: VerificationCode = VerificationCode.objects.filter(user=request.user,
                                                                      type=VerificationCode.EMAIL_CHANGE_TYPE,
                                                                      is_used=False)
            if len(Vcode) == 0:
                return Response({"message": "Проверочный код не найден или срок действия истек"},
                                status=status.HTTP_404_NOT_FOUND)
            Vcode = Vcode.first()

            if not Vcode.is_valid():
                return Response({"message": "Проверочный код не найден или срок действия истек"},
                                status=status.HTTP_404_NOT_FOUND)

            if Vcode.code != serializer.validated_data["code"]:
                return Response({"message": "Неверный проверочный код"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            request.user.email = Vcode.new_email
            request.user.save()

            return Response({"message": "Адрес электронной почты был изменен"}, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class TestDeleteView(generics.GenericAPIView):
    serializer_class = TestDeleteSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            CustomUser.objects.filter(email=serializer.validated_data['email']).delete()

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
