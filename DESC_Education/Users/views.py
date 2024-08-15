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
    EmptySerializer

)
from Users.smtp import send_auth_registration_code

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
                                    "firstName": "str",
                                    "lastName": "str",
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

            if not user.email_auth:
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

            if len(CustomUser.objects.filter(email=email)) != 0:
                return Response(
                    {'message': 'Email already registered'},
                    status=status.HTTP_406_NOT_ACCEPTABLE)

            user = CustomUser.objects.create_user(
                email=email,
                password=password
            )

            Vcode: VerificationCode = VerificationCode.objects.create(
                user=user,
                code=str(random.randint(1000, 9999))
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
                Vcode: VerificationCode = VerificationCode.objects.get(user=user)
            except VerificationCode.DoesNotExist:
                return Response({"message": "The verification code does not exist or did not match"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            if Vcode.code != code:
                return Response({"message": "The verification code does not exist or did not match"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

            if not Vcode.is_valid():
                return Response({"message": "The verification code has expired, request a new one"},
                                status=status.HTTP_403_FORBIDDEN)

            user.email_auth = True
            user.save()
            Vcode.is_used = True
            Vcode.save()

            return Response({"message": "User verified registration"},
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
                                    "firstName": "str",
                                    "lastName": "str",
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
