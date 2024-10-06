import random
from django.db import models
from Users.models import CustomUser
import uuid
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.apps import apps
from Files.models import File

class FilterCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
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


class TaskCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    filter_categories = models.ManyToManyField(FilterCategory, related_name='task_category')

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
    files = GenericRelation(File)
    # file = models.FileField(upload_to=user_task_directory_path)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, related_name='tasks')
    filters = models.ManyToManyField(Filter, related_name='tasks', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class TaskPattern(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, related_name='pattern_tasks')
    filters = models.ManyToManyField(Filter, related_name='pattern_tasks', blank=True)

    def __str__(self):
        return self.pattern_name

    class Meta:
        ordering = ['-title']



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
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solutions',
                             editable=False)
    status = models.CharField(max_length=10, choices=STATUSES, default=PENDING)

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='solutions')
    description = models.TextField(max_length=2000, null=True, blank=True)
    files = GenericRelation(File)
    company_comment = models.TextField(max_length=1000, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task.title} - {self.user.email}"


class Review(models.Model):
    RATING = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    solution = models.OneToOneField(Solution, related_name='review', on_delete=models.CASCADE)
    text = models.CharField(max_length=250)
    rating = models.IntegerField(choices=RATING, default=1)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


    class Meta:
        ordering = ['-created_at']