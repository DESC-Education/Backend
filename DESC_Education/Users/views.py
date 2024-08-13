from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.models import User
from Users.models import CustomUser
from rest_framework import serializers
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
    RegistrationSerializer
)
from Users.smtp import auth_register_mail


# Create your views here.


class HelloView(generics.GenericAPIView):
    serializer_class = None
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Hello, world!'})


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

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
                            'access_token': "string",
                            'refresh_token': "string",
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
            except User.DoesNotExist:
                return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(serializer.validated_data['password']):
                return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.email_auth:
                return Response({'message': 'Need to verify email'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)

            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh_token),
            },
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"},
                            status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

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
                            "message": "Need to verify email"
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


            CustomUser.objects.create_user(
                email=email,
                password=password
            )

            auth_register_mail(email)

            return Response({"message": "Authorization code sent to email"},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"},
                            status=status.HTTP_400_BAD_REQUEST)