import logging
from rest_framework import generics, status
from Tasks.permissions import IsCompanyRole
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from Tasks.serializers import (
    CategorySerializer,
    TaskSerializer,
    TaskDetailSerializer,
)
from Tasks.models import (
    Category,
    Task
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
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
