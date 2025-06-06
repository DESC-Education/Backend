from rest_framework import generics, status
from Settings.permissions import IsCompanyRole, IsStudentRole, EvaluateCompanyRole, IsCompanyOrStudentRole, IsAdminRole
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from Tasks.filters import TaskFilter, MyTasksFilter, SolutionFilter
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import filters
from django.db.models import Q
from Users.models import CustomUser
from django.utils import timezone
from Notifications.tasks import EventStreamSendNotification
from Notifications.models import Notification
from Settings.pagination import CustomPageNumberPagination
from Profiles.models import (
    StudentProfile
)
from Tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    SolutionSerializer,
    TaskCategorySerializer,
    FilterCategorySerializer,
    ReviewSerializer,
    ReviewListSerializer,
    # StudentTasksMySerializer,
    TaskCategoryWithFiltersSerializer,
    TaskPatternSerializer,
    EvaluateSolutionSerializer,
)
from Tasks.models import (
    Task,
    Solution,
    TaskCategory,
    FilterCategory,
    Filter,
    TaskPattern,
    Review
)


class TaskView(generics.GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsCompanyRole]

    @extend_schema(
        tags=["Tasks"],
        summary="Создание задания компанией"
    )
    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(user=request.user)

            return Response(TaskSerializer(instance).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    @extend_schema(
        tags=["Tasks"],
        summary="Получение списка заданий"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TaskDetailView(generics.GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsCompanyOrStudentRole]

    def get_object(self, pk):
        obj = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["Tasks"],
        summary="Изменение задания компанией"
    )
    def patch(self, request, pk):
        try:
            instance = self.get_object(pk)
            serializer = self.get_serializer(instance=instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            return Response(TaskSerializer(instance).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Tasks"],
        summary="Получение Задания по его ID"
    )
    def get(self, request, pk):
        instance = get_object_or_404(Task, pk=pk)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SolutionView(generics.GenericAPIView):
    serializer_class = SolutionSerializer
    permission_classes = [IsStudentRole]

    def get_object(self) -> StudentProfile:
        return get_object_or_404(StudentProfile, user=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Создание решения студентом"
    )
    def post(self, request):
        profile: StudentProfile = self.get_object()
        if profile.reply_count == 0:
            return Response({"message": "Недостаточно откликов для добавления решения"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)

        profile.reply_count -= 1
        profile.save()

        EventStreamSendNotification.delay(str(serializer.data.get('id')), Notification.SOLUTION_TYPE)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SolutionListView(generics.ListAPIView):
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [IsCompanyRole | IsAdminRole]
    filterset_class = SolutionFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(task__pk=self.pk)

        user: CustomUser = self.request.user
        if user.role == IsCompanyRole:
            queryset = queryset.filter(task__user=self.request.user)
        return queryset

    @extend_schema(
        tags=["Tasks"],
        summary="Получение списка решений по id task"
    )
    def get(self, request, pk, *args, **kwargs):
        self.request = request
        self.pk = pk
        return super().get(request, *args, **kwargs)


class SolutionDetailView(generics.GenericAPIView):
    serializer_class = SolutionSerializer
    permission_classes = [IsStudentRole | IsCompanyRole]

    def get_object(self, pk):
        obj = get_object_or_404(Solution, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["Tasks"],
        summary="Получение Решения по его ID",
    )
    def get(self, request, pk):
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCategoryListView(generics.ListAPIView):
    queryset = TaskCategory.objects.all().prefetch_related('filter_categories__filters')
    serializer_class = TaskCategoryWithFiltersSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров Task Category"
    )
    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CompanyTasksMyView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsCompanyRole]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MyTasksFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        task_status = self.request.query_params.get('status')
        now = timezone.now()
        if task_status == 'active':
            queryset = queryset.filter(deadline__gte=now)
        elif task_status == 'archived':
            queryset = queryset.filter(deadline__lt=now)

        return queryset

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров my Tasks",
        parameters=[
            OpenApiParameter(name='status', type=OpenApiTypes.STR, enum=['active', 'archive']),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StudentTasksMyView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsStudentRole]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MyTasksFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        task_status = self.request.query_params.get('status')
        now = timezone.now()
        if task_status == 'archived':
            queryset = queryset.filter(~Q(solutions__status=Solution.PENDING) | Q(deadline__lt=now))
        elif task_status == 'active':
            queryset = queryset.filter(solutions__status=Solution.PENDING, deadline__gte=now)

        return queryset

    def get_queryset(self):
        return Task.objects.filter(solutions__user=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров my Tasks",
        parameters=[
            OpenApiParameter(name='status', type=OpenApiTypes.STR, enum=['active', 'archive']),
        ]

    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TaskPatternPatternListView(generics.ListAPIView):
    queryset = TaskPattern.objects.all()
    serializer_class = TaskPatternSerializer
    permission_classes = [IsCompanyRole]

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров TaskPattern"
    )
    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EvaluateSolutionView(generics.GenericAPIView):
    serializer_class = EvaluateSolutionSerializer
    permission_classes = [EvaluateCompanyRole]

    def get_object(self, pk):
        obj = get_object_or_404(Solution, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["Tasks"],
        summary="Оценка решения компанией"
    )
    def post(self, request, pk):
        serializer = self.get_serializer(instance=self.get_object(pk), data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        solution_id = str(serializer.data.get('id'))
        EventStreamSendNotification.delay(solution_id, Notification.EVALUATION_TYPE)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ReviewCreateView(generics.GenericAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [EvaluateCompanyRole]

    def get_object(self, pk):
        instance = get_object_or_404(Solution, pk=pk)
        self.check_object_permissions(self.request, instance)
        return instance

    def check_permission(self, instance):
        if instance.task.user != self.request.user:
            raise PermissionDenied("Вы можете оставить отзыв только для решений своих заданий")

    @extend_schema(
        tags=["Tasks"],
        summary="Оставление отзыва о решении компанией"
    )
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.check_permission(serializer.validated_data.get('solution'))
        serializer.save()
        solution_id = str(serializer.data.get('id'))
        EventStreamSendNotification.delay(solution_id, Notification.REVIEW_TYPE)

        return Response(serializer.data, status=status.HTTP_200_OK)



class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewListSerializer
    permission_classes = [IsStudentRole]


    def get_queryset(self):
        return Review.objects.filter(solution__user=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Получение всех отзывов"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)