import random

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from django.contrib.auth.models import User
from Users.models import (
    CustomUser,
    VerificationCode,
)
from rest_framework import serializers
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
    ChangeEmailSerializer
)
from Users.smtp import (
    send_auth_registration_code,
    send_password_change_code,
    send_mail_change_code
)


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
                            "data": {
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
                            },
                            "message": "Successfull"
                        },
                    )
                ]
            ),
            401: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Неверные данные",
                        value={
                            "message": "Invalid email or password"
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
                            "message": "Need to verify email"
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
                            "message": "Other error message"
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
                return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(serializer.validated_data['password']):
                return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_verified:
                return Response({'message': 'Need to verify email'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            tokens = user.get_token()

            user_serializer = CustomUserSerializer(user)
            return Response({
                "data": {
                    "user": user_serializer.data,
                    "tokens": tokens
                },
                "message": "Successfull"
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
                            "message": "Authorization code sent to email"
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
                            "message": "Email already registered"
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
                            "message": "Other error message"
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
            password = serializer.validated_data['password']
            role = serializer.validated_data['role']

            if len(CustomUser.objects.filter(email=email)) != 0:
                return Response(
                    {'message': 'Email already registered'},
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

            send_auth_registration_code(email, Vcode.code)

            return Response({"message": "Authorization code sent to email"},
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
                            "data": {
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
                            },
                            "message": "User verified registration"
                        },
                    )
                ]
            ),
            403: OpenApiResponse(
                serializer_class,
                examples=[
                    OpenApiExample(
                        "Код истек",
                        value={
                            "message": "The verification code has expired, request a new one"
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
                            "message": "The user was not found"
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
                            "message": "The verification code does not exist or did not match"
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
                            "message": "Other error message"
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
                return Response({"message": "The user was not found"},
                                status=status.HTTP_404_NOT_FOUND)
            try:
                Vcode: VerificationCode = VerificationCode.objects.get(user=user,
                                                                       type=VerificationCode.REGISTRATION_TYPE,
                                                                       is_used=False)
            except VerificationCode.DoesNotExist:
                return Response({"message": "The verification code does not exist or did not match"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            if Vcode.code != code:
                return Response({"message": "The verification code does not exist or did not match"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            if not Vcode.is_valid():
                return Response({"message": "The verification code has expired, request a new one"},
                                status=status.HTTP_403_FORBIDDEN)

            user.is_verified = True
            user.save()
            Vcode.is_used = True
            Vcode.save()

            tokens = user.get_token()

            user_serializer = CustomUserSerializer(user)

            return Response({
                "data": {
                    "user": user_serializer.data,
                    "tokens": tokens
                },
                "message": "User verified registration"},
                            status=status.HTTP_200_OK)


        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    # serializer_class = EmptySerializer
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
                            "data": {
                                "user": {
                                    "id": "uuid",
                                    "email": "str",
                                    "role": "str",
                                    "isActive": "bool",
                                    "isStaff": "bool",
                                    "isSuperuser": "bool"
                                }
                            },
                            "message": "Success"
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
                            "message": "Other error message"
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

            return Response({
                "data": {
                    "user": serializer.data
                },
                "message": "Success"},
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
                            "message": "Verification code sent to email"
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
                            "message": "Other error message"
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
                            "message": "User is not authenticated."
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
                            "message": "User not found."
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
                            "message": "User already verified."
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
                            "message": "Code type incorrect."
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
                            return Response({"message": "User already verified"},
                                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

                    except CustomUser.DoesNotExist:
                        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                    try:
                        code: VerificationCode = VerificationCode.objects.get(user=user,
                                                                              type=VerificationCode.REGISTRATION_TYPE,
                                                                              is_used=False)
                        if code.is_valid():
                            return Response({"message": "The verification code is still active, try again later"},
                                            status=status.HTTP_409_CONFLICT)
                    except VerificationCode.DoesNotExist:
                        pass

                    Vcode_reg = VerificationCode.objects.create(user=user,
                                                                code=str(random.randint(1000, 9999)),
                                                                type=VerificationCode.REGISTRATION_TYPE)

                    send_auth_registration_code(email, Vcode_reg.code)

                    return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)

                case self.serializer_class.EMAIL_CHANGE_TYPE:
                    email = serializer.validated_data['email']

                    if not request.user.is_authenticated:
                        return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

                    Vcode_email = VerificationCode.objects.create(user=request.user,
                                                                  code=str(random.randint(1000, 9999)),
                                                                  type=VerificationCode.EMAIL_CHANGE_TYPE,
                                                                  new_email=email)
                    send_mail_change_code(email, Vcode_email.code)

                    return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)

                case self.serializer_class.PASSWORD_CHANGE_TYPE:
                    email = serializer.validated_data['email']
                    try:
                        user = CustomUser.objects.get(email=email)

                        if not user.is_verified:
                            return Response({"message": "User not verified"},
                                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

                    except CustomUser.DoesNotExist:
                        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

                    Vcode_pass = VerificationCode.objects.create(user=user,
                                                                 code=random.randint(1000, 9999),
                                                                 type=VerificationCode.PASSWORD_CHANGE_TYPE)

                    send_password_change_code(user.email, Vcode_pass.code)

                    return Response({"message": "Verification code sent to email"}, status=status.HTTP_200_OK)

                case _:
                    return Response({"message": "Code type incorrect"}, status=status.HTTP_406_NOT_ACCEPTABLE)

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
                            "message": "Password has been changed"
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
                            "message": "Other error message"
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
                            "message": "Verification code not found or expired"
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
                            "message": "Verification code is incorrect"
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
                            "message": "User not found"
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
                return Response({"message": "User not found"}, status=status.HTTP_409_CONFLICT)

            try:
                Vcode = VerificationCode.objects.get(user=user,
                                                     type=VerificationCode.PASSWORD_CHANGE_TYPE,
                                                     is_used=False)
            except VerificationCode.DoesNotExist:
                return Response({"message": "Verification code not found or expired"},
                                status=status.HTTP_404_NOT_FOUND)
            #
            if not Vcode.is_valid():
                return Response({"message": "Verification code not found or expired"},
                                status=status.HTTP_404_NOT_FOUND)
            #
            if Vcode.code != serializer.validated_data["code"]:
                return Response({"message": "Verification code is incorrect"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"message": "Password has been changed"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(generics.GenericAPIView):
    serializer_class = ChangeEmailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
                            "message": "Email has been changed"
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
                            "message": "Other error message"
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
                            "message": "Verification code not found or expired"
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
                            "message": "Verification code is incorrect"
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

            try:
                Vcode: VerificationCode = VerificationCode.objects.get(user=request.user,
                                                                       type=VerificationCode.EMAIL_CHANGE_TYPE,
                                                                       is_used=False)
            except VerificationCode.DoesNotExist:
                return Response({"message": "Verification code not found or expired"},
                                status=status.HTTP_404_NOT_FOUND)

            if not Vcode.is_valid():
                return Response({"message": "Verification code not found or expired"},
                                status=status.HTTP_404_NOT_FOUND)

            if Vcode.code != serializer.validated_data["code"]:
                return Response({"message": "Verification code is incorrect"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            request.user.email = Vcode.new_email
            request.user.save()

            return Response({"message": "Email has been changed"}, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
