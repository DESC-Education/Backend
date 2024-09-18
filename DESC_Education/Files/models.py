from django.db import models
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

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



class File(models.Model):
    VERIFICATION_FILE = 'verification_file'
    TASK_FILE = 'task_file'
    SOLUTION_FILE = 'solution_file'

    TYPE_CHOISES = [
        (VERIFICATION_FILE, "Файлы верификации"),
        (TASK_FILE, "Файлы задач"),
        (SOLUTION_FILE, "Файлы решений")
    ]

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    file = models.FileField(max_length=200, validators=[validate_file_type, validate_file_size])
    type = models.CharField(choices=TYPE_CHOISES, max_length=20)

    def save(self, *args, **kwargs):
        if self.type == self.VERIFICATION_FILE:
            self.file.name = f'users/{self.content_object.user.id}/verification_files/{self.file.name}'
        elif self.type == self.TASK_FILE:
            self.file.name = f'users/{self.content_object.user.id}/tasks/{self.content_object.id}/{self.file.name}'
        elif self.type == self.SOLUTION_FILE:
            self.file.name = f'users/{self.content_object.user.id}/solutions/{self.content_object.id}/{self.file.name}'

        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.file.name
