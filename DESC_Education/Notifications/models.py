from django.db import models
from Users.models import CustomUser
import uuid


class Notification(models.Model):
    VERIFICATION_TYPE = 'verification'
    EVALUATION_TYPE = 'evaluation'
    LEVEL_TYPE = 'level'
    REVIEW_TYPE = 'review'
    COUNT_RESET_TYPE = 'countReset'
    SOLUTION_TYPE = 'solution'

    TYPE_CHOICES = (
        (VERIFICATION_TYPE, 'Verification'),
        (EVALUATION_TYPE, 'Evaluation'),
        (LEVEL_TYPE, 'Level'),
        (REVIEW_TYPE, 'Review'),
        (COUNT_RESET_TYPE, 'Count Reset'),
        (SOLUTION_TYPE, 'Solution'),
    )


    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    title = models.CharField(max_length=250)
    message = models.TextField()
    payload = models.JSONField(null=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.message}"

    class Meta:
        ordering = ['-created_at']
