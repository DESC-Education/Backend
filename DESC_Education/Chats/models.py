from django.db import models
from Users.models import CustomUser
from django.utils import timezone
import uuid
from Tasks.models import (
    Task,
)


class Chat(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    members = models.ManyToManyField(CustomUser, through='ChatMembers')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class ChatMembers(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'chat')


class Message(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_created=True, editable=False)
    is_readed = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author}: \n{message}"
