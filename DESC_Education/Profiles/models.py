from django.db import models
from Users.models import CustomUser


# Create your models here.
class BaseProfile(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15)


