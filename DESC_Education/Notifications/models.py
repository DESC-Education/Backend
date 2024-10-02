from django.db import models
from Users.models import CustomUser
import uuid


class Notification(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    message = models.TextField()

    def __str__(self):
        return f"Notification for {self.user}: {self.message}"

    class Meta:
        ordering = ['-created_at']
