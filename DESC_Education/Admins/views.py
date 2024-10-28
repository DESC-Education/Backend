from django.shortcuts import render
from rest_framework import generics, status
from Settings.permissions import IsAdminRole
from Users.models import CustomUser
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, OuterRef, Subquery, F
from datetime import datetime
from django.db.models.functions import TruncDate
from Tasks.models import Task, Solution, TaskCategory, FilterCategory, Filter, TaskPattern
from Tasks.serializers import TaskListSerializer, SolutionSerializer
from Tasks.filters import MyTasksFilter, SolutionFilter
from Chats.models import Chat, Message, ChatMembers
from Chats.serializers import ChatListSerializer
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
    StatisticsUserSerializer,
    StatisticsTasksSerializer,
    AdminTaskCategorySerializer,
    AdminFilterSerializer,
    AdminFilterCategorySerializer,
    AdminTaskPatternSerializer
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiTypes,
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

        queryset = self.queryset.filter(date__gte=fromDate, date__lte=toDate)

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


class StatisticsTasksView(generics.GenericAPIView):
    serializer_class = StatisticsTasksSerializer
    queryset = Task.objects.annotate(date=TruncDate('created_at')).values('date').annotate(
        created=Count('id'),
    ).order_by('date')
    queryset2 = Solution.objects.annotate(date=TruncDate('created_at')).values('date').annotate(
        completed=Count('id', filter=Q(status=Solution.COMPLETED)),
        pending=Count('id', filter=Q(status=Solution.PENDING)),
        failed=Count('id', filter=Q(status=Solution.FAILED)),
    ).order_by('date')

    def get_queryset(self):
        results = []
        req_data = self.request.data

        fromDate = datetime.strptime(
            req_data.get('fromDate', (timezone.now() - timezone.timedelta(days=6)).strftime('%Y-%m-%d')),
            '%Y-%m-%d').date()

        toDate = datetime.strptime(
            req_data.get('toDate', timezone.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()

        queryset = self.queryset.filter(date__gte=fromDate, date__lte=toDate)
        queryset2 = self.queryset2.filter(date__gte=fromDate, date__lte=toDate)

        dates = [fromDate + timezone.timedelta(days=i) for i in range((toDate - fromDate).days + 1)]

        for date in dates:
            count_data = next((item for item in queryset if item['date'] == date), None)
            count_data2 = next((item for item in queryset2 if item['date'] == date), None)
            if count_data and count_data2:
                results.append({
                    'date': date,
                    'created': count_data['created'],
                    'completed': count_data2['completed'],
                    'pending': count_data2['pending'],
                    'failed': count_data2['failed'],
                })
            else:
                results.append({
                    'date': date,
                    'created': 0,
                    'solved': 0,
                    'pending': 0,
                    'failed': 0,
                })

        return results

    @extend_schema(
        tags=["Admins"],
        summary="Статистика заданий"
    )
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # print(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserChatsListView(generics.ListAPIView):
    serializer_class = ChatListSerializer

    # permission_classes = [IsAdminRole]
    # filter_backends = [SearchFilter, DjangoFilterBackend]
    # search_fields = ['companyprofile__last_name', ]

    def get_queryset(self, user):
        last_message_time = Message.objects.filter(chat=OuterRef('pk')).order_by('-created_at').values('created_at')[:1]
        queryset = (Chat.objects.filter(
            chatmembers__user=user)
                    .annotate(
            num_messages=Count('messages'),
            last_message_time=Subquery(last_message_time),
            is_favorite=Subquery(ChatMembers.objects.filter(chat=OuterRef('pk'),
                                                            user=user)
                                 .values('is_favorite')[:1])).filter(num_messages__gte=1)
                    .order_by(F('is_favorite').desc(nulls_last=True), F('last_message_time').desc(nulls_last=True)))

        return queryset

    @extend_schema(
        tags=["Admins"],
        summary="Получение списка чатов пользователя"
    )
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('pk')  # Получаем ID чата из URL параметров
        user = generics.get_object_or_404(CustomUser, pk=user_id)
        queryset = self.filter_queryset(self.get_queryset(user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            request = serializer.context['request']
            request.user = user

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        request = serializer.context['request']
        request.user = user
        return Response(serializer.data)


class AdminCompanyTasksListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    # permission_classes = [IsAdminRole]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MyTasksFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        task_status = self.request.query_params.get('status', 'active')
        now = timezone.now()
        if task_status == 'active':
            queryset = queryset.filter(deadline__gte=now)
        elif task_status == 'archived':
            queryset = queryset.filter(deadline__lt=now)

        return queryset

    def get_queryset(self):
        user_id = self.kwargs.get('pk')  # Получаем ID чата из URL параметров
        user = generics.get_object_or_404(CustomUser, pk=user_id)
        return Task.objects.filter(user=user)

    @extend_schema(
        tags=["Admins"],
        summary="Получение экземпляров заданий для компании",
        parameters=[
            OpenApiParameter(name='status', type=OpenApiTypes.STR, enum=['active', 'archive']),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminStudentSolutionsListView(generics.ListAPIView):
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    # permission_classes = [IsAdminRole]
    filter_backends = (DjangoFilterBackend,)

    # filterset_class = MyTasksFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        task_status = self.request.query_params.get('status', 'active')
        if task_status == 'archived':
            queryset = queryset.filter(~Q(status=Solution.PENDING))
        elif task_status == 'active':
            queryset = queryset.filter(status=Solution.PENDING)

        return queryset

    def get_queryset(self):
        user_id = self.kwargs.get('pk')  # Получаем ID чата из URL параметров
        user = generics.get_object_or_404(CustomUser, pk=user_id)
        return Solution.objects.filter(user=user)

    @extend_schema(
        tags=["Admins"],
        summary="Получение экземпляров заданий для студента",
        parameters=[
            OpenApiParameter(name='status', type=OpenApiTypes.STR, enum=['active', 'archive']),
        ]

    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminTaskCategoryListView(generics.ListCreateAPIView):
    queryset = TaskCategory.objects.all()
    serializer_class = AdminTaskCategorySerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение списка TaskCatogory"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Создание нового TaskCategory"
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdminTaskCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaskCategory.objects.all()
    serializer_class = AdminTaskCategorySerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение TaskCategory по его id"
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Полное обновление TaskCategory"
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Частичное Обновление TaskCategory"
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Удаление TaskCategory"
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)




class AdminFilterCategoryListView(generics.ListCreateAPIView):
    queryset = FilterCategory.objects.all()
    serializer_class = AdminFilterCategorySerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение списка FilterCategory"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Создание нового FilterCategory"
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdminFilterCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FilterCategory.objects.all()
    serializer_class = AdminFilterCategorySerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение FilterCategory по его id"
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Полное обновление FilterCategory"
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Частичное Обновление FilterCategory"
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Удаление FilterCategory"
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)



class AdminFilterListView(generics.ListCreateAPIView):
    queryset = Filter.objects.all()
    serializer_class = AdminFilterSerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение списка Filter"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Создание нового Filter"
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)





class AdminFilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Filter.objects.all()
    serializer_class = AdminFilterSerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение Filter по его id"
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Полное обновление Filter"
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Частичное Обновление Filter"
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Удаление Filter"
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)




class AdminTaskPatternListView(generics.ListCreateAPIView):
    queryset = TaskPattern.objects.all()
    serializer_class = AdminTaskPatternSerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение списка TaskPattern"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Создание нового TaskPattern"
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)




class AdminTaskPatternDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaskPattern.objects.all()
    serializer_class = AdminTaskPatternSerializer

    @extend_schema(
        tags=["Admins"],
        summary="Получение TaskPattern по его id"
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Полное обновление TaskPattern"
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Частичное Обновление TaskPattern"
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Admins"],
        summary="Удаление TaskPattern"
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)