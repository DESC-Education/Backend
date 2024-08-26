import random
from django.db import models
from Users.models import CustomUser
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.apps import apps


def user_task_directory_path(instance, filename):
    return f'users/{instance.user.id}/tasks/{instance.id}/{filename}'


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    deadline = models.DateTimeField()
    file = models.FileField(upload_to=user_task_directory_path)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Filter(models.Model):
    category = models.ForeignKey(Category, related_name='filters', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
