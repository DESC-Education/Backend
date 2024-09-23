from django.shortcuts import render
from rest_framework import generics, status
from Settings.permissions import IsAdminRole
from Users.models import CustomUser
from rest_framework.response import Response
from django.db.models import Q
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
    ProfileVerifyRequestDetailSerializer,
    CustomUserListSerializer
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    OpenApiRequest,
    inline_serializer)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from Admins.filters import (
    ProfileVerifyRequestFilter,
    CustomUserListFilter
)
from Users.models import CustomUser


class AdminProfileVerifyRequestListView(generics.ListAPIView):
    queryset = ProfileVerifyRequest.objects.all().prefetch_related('profile__user')
    serializer_class = ProfileVerifyRequestsListSerializer
    # permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['student_profile__first_name', 'student_profile__last_name',
                     'company_profile__first_name', 'company_profile__last_name']
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


class AdminCustomUserListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(Q(role=CustomUser.STUDENT_ROLE) | Q(role=CustomUser.COMPANY_ROLE))\
        .select_related('companyprofile').select_related('studentprofile')
    serializer_class = CustomUserListSerializer
    # permission_classes = [IsAdminRole]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['companyprofile__first_name', 'companyprofile__last_name',
                     'studentprofile__first_name', 'studentprofile__last_name',
                     'email']
    filterset_class = CustomUserListFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            queryset = CustomUser.objects.all()
        return queryset

    @extend_schema(
        tags=["Admins"],
        summary="Получение списка пользователей"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
