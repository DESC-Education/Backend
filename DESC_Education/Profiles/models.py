import random
from django.utils import timezone as tz
from django.db import models
from Users.models import CustomUser
from Tasks.models import Task, Solution
from django.apps import apps
import uuid
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from Files.models import (
    File
)


def image_upload_to(instance, filename):
    return f'users/{instance.user.id}/logo/{filename}'


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

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    profile = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


# Create your models here.
class BaseProfile(models.Model):
    VERIFIED = "verified"
    ON_VERIFICATION = "on_verification"
    NOT_VERIFIED = "not_verified"
    REJECTED = "rejected"

    VERIFICATION_CHOISES = [
        (VERIFIED, "Профиль подтвержден"),
        (ON_VERIFICATION, "Профиль на проверке"),
        (NOT_VERIFIED, "Профиль не подтвержден"),
        (REJECTED, "Профиль не прошел проверку")
    ]
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, editable=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, blank=True)
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
    verification_files = GenericRelation(File)
    skills = models.ManyToManyField(Skill, blank=True)
    verification = models.CharField(max_length=20, choices=VERIFICATION_CHOISES, default=NOT_VERIFIED)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.email

    def get_verification_status(self):
        statuses = {
            ProfileVerifyRequest.APPROVED: self.VERIFIED,
            ProfileVerifyRequest.REJECTED: self.REJECTED,
            ProfileVerifyRequest.PENDING: self.ON_VERIFICATION
        }
        if self.verification == self.VERIFIED:
            return {"status": self.VERIFIED}

        v_requests: ProfileVerifyRequest = self.verification_requests

        if v_requests.exists():
            v_request: ProfileVerifyRequest = v_requests.first()
            if v_request.status == ProfileVerifyRequest.REJECTED:
                return {
                    'status': v_request.status,
                    'comment': v_request.comment
                }
            elif v_request.status == ProfileVerifyRequest.APPROVED:
                if self.verification != self.VERIFIED:
                    self.verification = self.VERIFIED
                    self.save()
                return {"status": self.VERIFIED}

            return {"status": statuses.get(v_request.status)}

        return {"status": self.NOT_VERIFIED}


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


class StudentProfileManager(models.Manager):
    def create(self, *args, **kwargs):
        instance = super().create(*args, **kwargs)
        instance.get_reply_count()
        return instance


def get_default_reply_reload_date():
    return timezone.now() + timezone.timedelta(days=StudentProfile.REPLY_RELOAD_DAYS)


class StudentProfile(BaseProfile):
    REPLY_MONTH_COUNT = 30
    REPLY_RELOAD_DAYS = 30

    FULL_TIME_EDUCATION = "full_time"
    PART_TIME_EDUCATION = "part_time"
    FULL_TIME_AND_PART_TIME_EDUCATION = "full_part_time"

    EDUCATION_CHOISES = [
        (FULL_TIME_EDUCATION, "Очная форма обучения"),
        (PART_TIME_EDUCATION, "Заочная форма обучения"),
        (FULL_TIME_AND_PART_TIME_EDUCATION, "Очно-Заочная форма обучения")
    ]

    BEGINNER_LEVEL = 1
    ADVANCED_LEVEL = 2
    EXPERIENCE_LEVEL = 3

    LEVEL_CHOICES = [
        (BEGINNER_LEVEL, 'Начинающий'),
        (ADVANCED_LEVEL, 'Продвинутый'),
        (EXPERIENCE_LEVEL, 'Опытный')
    ]
    verification_requests = GenericRelation(ProfileVerifyRequest, related_name="v_requests",
                                            related_query_name="student_profile")
    profession = models.CharField(max_length=150, null=True)
    form_of_education = models.CharField(choices=EDUCATION_CHOISES, max_length=15, null=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True, related_name='university')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, related_name='faculty')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, null=True, related_name='specialty')
    admission_year = models.IntegerField(null=True)
    reply_count = models.IntegerField(default=REPLY_MONTH_COUNT, editable=False, blank=True)
    reply_reload_date = models.DateTimeField(default=get_default_reply_reload_date, editable=False,
                                             blank=True)
    level_id = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=BEGINNER_LEVEL, editable=False)

    objects = StudentProfileManager()

    def get_reply_count(self):
        now = tz.now()
        if now >= self.reply_reload_date:
            self.reply_count = self.REPLY_MONTH_COUNT
            self.reply_reload_date = now + tz.timedelta(days=self.REPLY_RELOAD_DAYS)
            self.save()

            from Notifications.tasks import EventStreamSendNotification
            from Notifications.models import Notification
            EventStreamSendNotification.delay(self.user.id, Notification.COUNT_RESET_TYPE)

        return self.reply_count

    def check_level(self):
        solved_tasks_count = Task.objects.filter(solutions__user=self.user,
                                                 solutions__status=Solution.COMPLETED)
        level_before = self.level_id
        if solved_tasks_count.count() < 15:
            self.level_id = self.BEGINNER_LEVEL
        elif solved_tasks_count.count() < 30:
            self.level_id = self.ADVANCED_LEVEL
        elif solved_tasks_count.count() <= 60:
            self.level_id = self.EXPERIENCE_LEVEL

        if level_before != self.level_id:
            from Notifications.tasks import EventStreamSendNotification
            from Notifications.models import Notification

            EventStreamSendNotification.delay(self.user.id, Notification.LEVEL_TYPE,)



        self.save()


class CompanyProfile(BaseProfile):
    link_to_company = models.URLField()
    company_name = models.CharField(max_length=100)
    verification_requests = GenericRelation(ProfileVerifyRequest, related_name="v_requests",
                                            related_query_name="company_profile")
