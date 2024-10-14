import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils import timezone
from django.db.utils import IntegrityError
# Create your models here.
from django.db.models import Q
from django.apps import apps


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        try:
            deleted_user = self.get(Q(email=email) & ~Q(deleted_at=None))
            deleted_user.email = f'deleted_user_{email}'
            deleted_user.save(using=self._db)
        except:
            pass

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if user.role == CustomUser.STUDENT_ROLE:
            profile = apps.get_model('Profiles.StudentProfile')
            profile.objects.create(user=user)
        elif user.role == CustomUser.COMPANY_ROLE:
            profile = apps.get_model('Profiles.CompanyProfile')
            profile.objects.create(user=user)

        return user


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

    def get_queryset(self):
        queryset = super().get_queryset().filter(deleted_at=None)
        return queryset


class AllUsersManager(BaseUserManager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class CustomUser(AbstractBaseUser):
    STUDENT_ROLE = "student"
    COMPANY_ROLE = "company"
    ADMIN_ROLE = "admin"
    UNIVERSITY_ADMIN_ROLE = "u_admin"

    ROLE_CHOISES = [
        (STUDENT_ROLE, "Student Role"),
        (COMPANY_ROLE, "Company Role"),
        (ADMIN_ROLE, "Admin Role"),
        (UNIVERSITY_ADMIN_ROLE, "University Admin Role")
    ]

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    email = models.EmailField(db_index=True, unique=True)
    role = models.CharField(max_length=7, choices=ROLE_CHOISES, default=STUDENT_ROLE)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, editable=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, default=None)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()
    all_objects = AllUsersManager()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.email

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.email = f"deleted_user_{self.email}"
        self.save()

    @staticmethod
    def has_perm(perm, obj=None):
        return True

    @staticmethod
    def has_module_perms(app_label):
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
            'id': self.id,
            'email': self.email,
        }

    def get_profile(self):
        if self.role == self.STUDENT_ROLE:
            return self.studentprofile
        elif self.role == self.COMPANY_ROLE:
            return self.companyprofile
        else:
            return None

    def get_full_name(self):
        profile = self.get_profile()
        return f"{profile.first_name} {profile.last_name}"


class VerificationCode(models.Model):
    REGISTRATION_TYPE = "RG"
    PASSWORD_CHANGE_TYPE = "PW"
    EMAIL_CHANGE_TYPE = "EM"

    TYPE_CHOISES = [
        (REGISTRATION_TYPE, "Registration Code"),
        (PASSWORD_CHANGE_TYPE, "Password Code"),
        (EMAIL_CHANGE_TYPE, "Email Code")
    ]

    EXPIRED_SECONDS = 300

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    new_email = models.EmailField(null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.IntegerField()
    type = models.CharField(max_length=2, choices=TYPE_CHOISES)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, editable=False)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return (timezone.now() - self.created_at).total_seconds() < self.EXPIRED_SECONDS and not self.is_used

    def get_time(self):
        return (timezone.now() - self.created_at).total_seconds()

    class Meta:
        ordering = ['-created_at']
