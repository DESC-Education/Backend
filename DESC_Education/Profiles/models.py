from django.db import models
from Users.models import CustomUser
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


class City(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    name = models.CharField(unique=True, max_length=100)
    region = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


class University(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    name = models.CharField(unique=True, max_length=200)
    short_name = models.CharField(max_length=100)

    # region = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


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


def image_upload_to(instance, filename):
    # match image_type:
    #     case "logo":
    #         return f'logo_imgs/{filename}'
    #     case "":
    #         assert Exception("Invalid image type")
    return f'logo_imgs/{filename}'


def student_card_upload(instance, filename):
    return f'student_cards/{filename}'


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
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    phone_visibility = models.BooleanField()
    email_visibility = models.BooleanField()
    logo_img = models.ImageField(upload_to=image_upload_to, width_field=220, height_field=220, blank=True, null=True)
    telegram_link = models.URLField(blank=True, null=True)
    vk_link = models.URLField(blank=True, null=True)
    timezone = models.IntegerField()
    is_verified = models.BooleanField(default=False)
    verification_requests = GenericRelation(ProfileVerifyRequest)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.email


class StudentProfile(BaseProfile):
    FULL_TIME_EDUCATION = "full_time"
    PART_TIME_EDUCATION = "part_time"
    FULL_TIME_AND_PART_TIME_EDUCATION = "full_part_time"

    EDUCATION_CHOISES = [
        (FULL_TIME_EDUCATION, "Очная форма обучения"),
        (PART_TIME_EDUCATION, "Заочная форма обучения"),
        (FULL_TIME_AND_PART_TIME_EDUCATION, "Очно-Заочная форма обучения")
    ]

    form_of_education = models.CharField(choices=EDUCATION_CHOISES, max_length=15)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=50, )
    admission_year = models.IntegerField()
    student_card = models.ImageField(upload_to=student_card_upload)


class CompanyProfile(BaseProfile):
    link_to_company = models.URLField()
    company_name = models.CharField(max_length=100)
