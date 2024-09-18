from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from Files.models import (
    File
)



class CustomFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    type = serializers.ChoiceField(File.TYPE_CHOISES)

    class Meta:
        model = File
        fields = ('file', 'type')

    @staticmethod
    def validate_file(value):
        # Проверка расширения файла
        valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.docx']
        extension = value.name.split('.')[-1]
        if f'.{extension}' not in valid_extensions:
            raise serializers.ValidationError('Неверное расширение файла. Разрешены только: jpg, jpeg, png, pdf, docx')

        # Проверка размера файла
        max_file_size = 5 * 1024 * 1024  # 5 МБ
        if value.size > max_file_size:
            raise serializers.ValidationError('Размер файла не должен превышать 5 МБ.')

        return value
