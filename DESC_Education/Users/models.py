import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils import timezone

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault("email_auth", True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email_auth = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


    def get_token(self):
        access_token = AccessToken.for_user(self)
        refresh_token = RefreshToken.for_user(self)

        return {
            'accessToken': str(access_token),
            'refreshToken': str(refresh_token),
        }

    @property
    def token_payload(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }


class VerificationCode(models.Model):
    REGISTRATION_TYPE = "RG"
    PASSWORD_TYPE = "PW"
    EMAIL_TYPE = "EM"

    TYPE_CHOISES = [
        (REGISTRATION_TYPE, "Registration Code"),
        (PASSWORD_TYPE, "Password Code"),
        (EMAIL_TYPE, "Email Code")
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    type = models.CharField(max_length=2, choices=TYPE_CHOISES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):

        return (timezone.now() - self.created_at).total_seconds() < 60 * 30 and not self.is_used



