from django.shortcuts import render
from rest_framework import generics
from Settings.permissions import IsAdminRole
from Users.models import CustomUser
from Profiles.models import (
    BaseProfile,
    StudentProfile,
    CompanyProfile,
    University,
    ProfileVerifyRequest,
)
from Admins.serializers import (
    ProfileVerifyRequestsListSerializer
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    OpenApiRequest,
    inline_serializer)
from django_filters.rest_framework import DjangoFilterBackend
from Admins.filters import ProfileVerifyRequestFilter


class AdminProfileVerifyRequestsView(generics.ListAPIView):
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





