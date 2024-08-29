import random

from django.db import models
from Users.models import CustomUser
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


def image_upload_to(instance, filename):
    return f'users/{instance.user.id}/logo/{filename}'


def verification_files_upload(instance, filename):
    return f'users/{instance.profile.user.id}/verification_files/{filename}'


class City(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True)
    name = models.CharField(unique=True, max_length=100)
    region = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class Skill(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class PhoneVerificationCode(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    phone = models.CharField(max_length=15)
    code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, editable=False, blank=True)


    @staticmethod
    def create_code():
        return random.randint(111111, 999999)

    def __str__(self):
        return self.phone

    class Meta:
        ordering = ['-created_at']



class University(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True)
    name = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class Faculty(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    name = models.CharField(max_length=200)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class ProfileVerifyRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    profile = GenericForeignKey(ct_field='content_type', fk_field='object_id')

    request_date = models.DateTimeField(auto_now_add=True, editable=False, blank=True)
    status = models.CharField(max_length=20, choices=[
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ], default=PENDING)
    comments = models.TextField(null=True, blank=True)


class File(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    profile = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    file = models.FileField(upload_to=verification_files_upload, max_length=200)


# Create your models here.
class BaseProfile(models.Model):
    VERIFIED = "verified"
    ON_VERIFICATION = "on_verification"
    NOT_VERIFIED = "not_verified"
    NOT_ACCEPTED = "not_accepted"

    VERIFICATION_CHOISES = [
        (VERIFIED, "Профиль подтвержден"),
        (ON_VERIFICATION, "Профиль на проверке"),
        (NOT_VERIFIED, "Профиль не подтвержден"),
        (NOT_ACCEPTED, "Профиль не прошел проверку")
    ]
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, editable=False, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    phone_visibility = models.BooleanField(default=True)
    email_visibility = models.BooleanField(default=True)
    logo_img = models.ImageField(upload_to=image_upload_to, blank=True, null=True)
    telegram_link = models.URLField(blank=True, null=True)
    vk_link = models.URLField(blank=True, null=True)
    timezone = models.IntegerField(null=True)
    is_verified = models.BooleanField(default=False)
    verification_requests = GenericRelation(ProfileVerifyRequest, related_name="v_requests")
    verification_files = GenericRelation(File, related_name='v_files')
    skills = models.ManyToManyField(Skill, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.email


class Specialty(models.Model):
    BACHELOR = "bachelor"
    MAGISTRACY = "magistracy"
    SPECIALTY = "specialty"
    EDUCATION_PROGRAMS = [
        (BACHELOR, "Бакалавриат"),
        (MAGISTRACY, "Магистратура"),
        (SPECIALTY, "Специалитет")
    ]
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)
    type = models.CharField(choices=EDUCATION_PROGRAMS, max_length=11, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class StudentProfile(BaseProfile):
    FULL_TIME_EDUCATION = "full_time"
    PART_TIME_EDUCATION = "part_time"
    FULL_TIME_AND_PART_TIME_EDUCATION = "full_part_time"

    EDUCATION_CHOISES = [
        (FULL_TIME_EDUCATION, "Очная форма обучения"),
        (PART_TIME_EDUCATION, "Заочная форма обучения"),
        (FULL_TIME_AND_PART_TIME_EDUCATION, "Очно-Заочная форма обучения")
    ]

    form_of_education = models.CharField(choices=EDUCATION_CHOISES, max_length=15, null=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True, related_name='university')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, related_name='faculty')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, null=True, related_name='specialty')
    admission_year = models.IntegerField(null=True)


class CompanyProfile(BaseProfile):
    link_to_company = models.URLField()
    company_name = models.CharField(max_length=100)
