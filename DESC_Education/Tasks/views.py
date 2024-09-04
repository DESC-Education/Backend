from rest_framework import generics, status
from Settings.permissions import IsCompanyRole, IsStudentRole
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
# from Tasks.filters import CategoryFilterBackend
from rest_framework import filters
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
    CompanyTasksMySerializer,
    StudentTasksMySerializer,
    TaskCategoryWithFiltersSerializer,
    TaskPatternSerializer
)
from Tasks.models import (
    Task,
    Solution,
    TaskCategory,
    FilterCategory,
    Filter,
    TaskPattern
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

    @extend_schema(
        tags=["Tasks"],
        summary="Получение списка заданий"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TaskDetailView(generics.GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsCompanyRole]

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
            serializer = self.get_serializer(data=request.data, instance=instance)
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
        instance = self.get_object(pk)
        return Response(TaskSerializer(instance).data, status=status.HTTP_200_OK)


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

        return Response(serializer.data, status=status.HTTP_200_OK)


class SolutionDetailView(generics.GenericAPIView):
    serializer_class = SolutionSerializer
    permission_classes = [IsStudentRole]

    def get_object(self, pk):
        obj = get_object_or_404(Solution, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["Tasks"],
        summary="Получение Решения по его ID"
    )
    def get(self, request, pk):
        instance = self.get_object(pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)



class TaskCategoryListView(generics.ListAPIView):
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategoryWithFiltersSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров Task Category"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CompanyTasksMyView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = CompanyTasksMySerializer
    permission_classes = [IsCompanyRole]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров my Tasks"
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer()
        return Response(serializer.to_representation(queryset))


class StudentTasksMyView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = StudentTasksMySerializer
    permission_classes = [IsStudentRole]

    def get_queryset(self):
        return Solution.objects.filter(user=self.request.user)

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров my Tasks"
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer()
        return Response(serializer.to_representation(queryset))


class TaskPatternPatternListView(generics.ListAPIView):
    queryset = TaskPattern.objects.all()
    serializer_class = TaskPatternSerializer
    permission_classes = [IsCompanyRole]

    @extend_schema(
        tags=["Tasks"],
        summary="Получение экземпляров TaskPattern"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

