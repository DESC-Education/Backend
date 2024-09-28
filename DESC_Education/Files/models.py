from django.db import models
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.conf import settings
import os


def validate_file_type(value):
    valid_extensions = ['.pdf', '.jpg', '.png']
    if not any(value.name.endswith(ext) for ext in valid_extensions):
        raise ValidationError('Неподдерживаемое расширение файла.')
    else:
        print(f"File type is acceptable: {value.name}")


def validate_file_size(value):
    limit = 5 * 1024 * 1024  # 5 MB
    if value.size > limit:
        raise ValidationError('Максмальный размер файла 5 MB.')
    else:
        print(f"File size is acceptable: {value.size}")


def get_file_path(instance, filename):
    match instance.type:
        case instance.VERIFICATION_FILE:
            return f'users/{instance.content_object.user.id}/verification_files/{filename}'
        case instance.TASK_FILE:
            return f'users/{instance.content_object.user.id}/tasks/{instance.content_object.id}/{filename}'
        case instance.SOLUTION_FILE:
            return f'users/{instance.content_object.user.id}/solutions/{instance.content_object.id}/{filename}'
        case instance.CHAT_FILE:
            return f'chats/{instance.content_object.id}/{filename}'


class File(models.Model):
    VERIFICATION_FILE = 'verification_file'
    TASK_FILE = 'task_file'
    SOLUTION_FILE = 'solution_file'
    CHAT_FILE = 'chat_file'


    TYPE_CHOISES = [
        (VERIFICATION_FILE, "Файлы верификации"),
        (TASK_FILE, "Файлы задач"),
        (SOLUTION_FILE, "Файлы решений"),
        (CHAT_FILE, "Файлы чатов"),
    ]

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    file = models.FileField(upload_to=get_file_path, max_length=200, validators=[validate_file_type, validate_file_size])
    type = models.CharField(choices=TYPE_CHOISES, max_length=20)


    def __str__(self):
        return self.file.name
