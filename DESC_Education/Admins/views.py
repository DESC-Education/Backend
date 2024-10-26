from django.shortcuts import render
from rest_framework import generics, status
from Settings.permissions import IsAdminRole
from Users.models import CustomUser
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime
from django.db.models.functions import TruncDate
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
    CustomUserListSerializer,
    CustomUserDetailSerializer,
    StatisticsUserSerializer
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
    queryset = CustomUser.objects.filter(Q(role=CustomUser.STUDENT_ROLE) | Q(role=CustomUser.COMPANY_ROLE)) \
        .select_related('companyprofile').select_related('studentprofile')
    serializer_class = CustomUserListSerializer
    # permission_classes = [IsAdminRole]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['companyprofile__first_name', 'companyprofile__last_name', 'companyprofile__company_name',
                     'studentprofile__first_name', 'studentprofile__last_name',
                     'email', ]
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


class AdminCustomUserDetailView(generics.GenericAPIView):
    serializer_class = CustomUserDetailSerializer
    # permission_classes = [IsAdminRole]

    def get_object(self, pk):
        obj = get_object_or_404(CustomUser, pk=pk)
        return obj

    @extend_schema(
        tags=["Admins"],
        summary="Получение экземпляра пользователя"
    )
    def get(self, request, pk):
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StatisticsUserView(generics.GenericAPIView):
    serializer_class = StatisticsUserSerializer
    queryset = CustomUser.objects.annotate(date=TruncDate('created_at')).values('date').annotate(
        students=Count('id', filter=Q(role=CustomUser.STUDENT_ROLE)),
        companies=Count('id', filter=Q(role=CustomUser.COMPANY_ROLE))
    ).order_by('date')

    # permission_classes = [IsAdminRole]


    def get_queryset(self):
        results = []
        req_data = self.request.data

        fromDate = datetime.strptime(
            req_data.get('fromDate', (timezone.now() - timezone.timedelta(days=6)).strftime('%Y-%m-%d')),
            '%Y-%m-%d').date()

        toDate = datetime.strptime(
            req_data.get('toDate', timezone.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()

        queryset = self.queryset.filter()

        dates = [fromDate + timezone.timedelta(days=i) for i in range((toDate - fromDate).days + 1)]

        for date in dates:
            count_data = next((item for item in queryset if item['date'] == date), None)
            if count_data:
                results.append({
                    'date': date,
                    'students': count_data['students'],
                    'companies': count_data['companies']
                })
            else:
                results.append({
                    'date': date,
                    'students': 0,
                    'companies': 0
                })

        return results

    @extend_schema(
        tags=["Admins"],
        summary="Статистика регистраций пользователей"
    )
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
