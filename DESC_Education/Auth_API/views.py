from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes
from Auth_API.serializers import (
    LoginSerializer,
    RegistrationSerializer
)


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

        request=serializer_class,
        responses={
            200: OpenApiResponse(
                description='User authenticated successfully.',
                examples=[
                    OpenApiExample(
                        name='Example response',
                        value={
                            'access_token': 'your_access_token',
                            'refresh_token': 'your_refresh_token'
                        }
                    )
                ],
            ),
            401: OpenApiResponse(description='Invalid email or password')
        }

    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(serializer.validated_data['password']):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)

        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        },
            status=status.HTTP_200_OK)


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        return Response({"status": 1}, mess)
