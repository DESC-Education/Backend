from rest_framework import serializers
from django.conf import settings
from django.apps import apps
from django.utils import timezone
from Files.models import (
    File
)


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    name = serializers.SerializerMethodField()
    extension = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ('id', 'size', 'file', 'name', 'extension', 'path')

    @staticmethod
    def get_size(obj):
        return obj.file.size

    @staticmethod
    def get_name(obj) -> str:
        return obj.file.name.split('/')[-1].rsplit('.', 1)[0]

    @staticmethod
    def get_path(obj) -> str:
        return obj.file.url

    @staticmethod
    def get_extension(obj) -> str:
        return obj.file.name.split('.')[-1]

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
