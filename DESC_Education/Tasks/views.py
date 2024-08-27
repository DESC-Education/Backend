import logging
from rest_framework import generics, status
from Tasks.permissions import IsCompanyRole
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from Settings.pagination import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from Tasks.serializers import (
    TaskSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskCreateSerializer
)
from Tasks.models import (
    Task
)


class TaskView(generics.GenericAPIView):
    serializer_class = TaskCreateSerializer
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
    serializer_class = TaskDetailSerializer
    permission_classes = [IsCompanyRole]

    def get_object(self, pk):
        return get_object_or_404(Task, pk=pk)

    @extend_schema(
        tags=["Tasks"],
        summary="Изменение задания компанией"
    )
    def patch(self, request, pk):
        try:
            instance = self.get_object(pk)
            self.check_object_permissions(request, instance)
            serializer = self.get_serializer(data=request.data, instance=instance)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            return Response(TaskSerializer(instance).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
