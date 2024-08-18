from django.db import models
from Users.models import CustomUser
import uuid


def image_upload_to(instance, filename):
    # match image_type:
    #     case "logo":
    #         return f'logo_imgs/{filename}'
    #     case "":
    #         assert Exception("Invalid image type")
    print(instance)
    return f'logo_imgs/{filename}'


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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15)
    phone_visibility = models.BooleanField(default=False)
    email_visibility = models.BooleanField(default=False)
    logo_img = models.ImageField(upload_to=image_upload_to, width_field=220, height_field=220, blank=True, null=True)
    telegram_link = models.CharField(blank=True, null=True)
    vk_link = models.CharField(blank=True, null=True)
    timezone = models.IntegerField()
    verification = models.CharField(choices=VERIFICATION_CHOISES, default=NOT_VERIFIED)

    class Meta:
        abstract = True


class University(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    name = models.CharField(unique=True)
    short_name = models.CharField()

    # region = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


class StudentProfile(BaseProfile):
    FULL_TIME_EDUCATION = "full_time"
    PART_TIME_EDUCATION = "part_time"
    FULL_TIME_AND_PART_TIME_EDUCATION = "full_part_time"

    EDUCATION_CHOISES = [
        (FULL_TIME_EDUCATION, "Очная форма обучения"),
        (PART_TIME_EDUCATION, "Заочная форма обучения"),
        (FULL_TIME_AND_PART_TIME_EDUCATION, "Очно-Заочная форма обучения")
    ]

    form_of_education = models.CharField(choices=EDUCATION_CHOISES)
    university = models.OneToOneField(University, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=50,)
    admission_year = models.IntegerField()


class CompanyProfile(BaseProfile):
    link_to_company = models.CharField(null=True)


class City(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    name = models.CharField(unique=True, max_length=100)
    region = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name
