import random
from django.db import models
from Users.models import CustomUser
import uuid
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.apps import apps


class TaskCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class FilterCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    task_category = models.ManyToManyField(TaskCategory, related_name='filter_categories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class Filter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    filter_category = models.ForeignKey(FilterCategory, related_name='filters', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


def user_task_directory_path(instance, filename):
    return f'users/{instance.user.id}/tasks/{instance.id}/{filename}'


def user_solution_directory_path(instance, filename):
    return f'users/{instance.user.id}/solutions/{instance.id}/{filename}'


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    deadline = models.DateTimeField()
    file = models.FileField(upload_to=user_task_directory_path)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, related_name='tasks')
    filters = models.ManyToManyField(Filter, related_name='tasks', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Solution(models.Model):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"

    STATUSES = [
        (COMPLETED, "Выполнено"),
        (FAILED, "Не выполнено"),
        (PENDING, "На рассмотрении"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='solutions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solutions')
    description = models.TextField(max_length=2000)
    file = models.FileField(upload_to=user_solution_directory_path)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUSES, default=PENDING)
    company_comment = models.TextField(max_length=1000, blank=True, null=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task.title} - {self.user.email}"