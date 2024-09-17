from django.shortcuts import render
from rest_framework import generics, status
from Settings.permissions import IsAdminRole
from Users.models import CustomUser
from rest_framework.response import Response
from Profiles.models import (
    BaseProfile,
    StudentProfile,
    CompanyProfile,
    University,
    ProfileVerifyRequest,
)
from django.shortcuts import get_object_or_404
from Admins.serializers import (
    ProfileVerifyRequestsListSerializer,
    ProfileVerifyRequestDetailSerializer
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    OpenApiRequest,
    inline_serializer)
from django_filters.rest_framework import DjangoFilterBackend
from Admins.filters import (
    ProfileVerifyRequestFilter,

)


class AdminProfileVerifyRequestListView(generics.ListAPIView):
    queryset = ProfileVerifyRequest.objects.all()
    serializer_class = ProfileVerifyRequestsListSerializer
    # permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfileVerifyRequestFilter


    @extend_schema(
        tags=["Admins"],
        summary="Получение экземпляров ProfileVerifyRequest"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminProfileVerifyRequestDetailView(generics.GenericAPIView):
    serializer_class = ProfileVerifyRequestDetailSerializer
    # permission_classes = [IsAdminRole]


    def get_object(self, pk):
        obj = get_object_or_404(ProfileVerifyRequest, pk=pk)
        return obj

    @extend_schema(
        tags=["Admins"],
        summary="Получение экземпляра ProfileVerifyRequest"
    )
    def get(self, request, pk):
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Admins"],
        summary="Верификация ProfileVerifyRequest"
    )

    def post(self, request, pk):
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(admin=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)









