from django.db import migrations
import requests
import csv


def get_task_categories(apps, schema_editor):
    TaskCategory = apps.get_model('Tasks', 'TaskCategory')

    task_category_data = [
        {"id": "c8ce70d4-6d74-460e-935a-2ae229e633c9", "name": "Анимация"},
        {"id": "bedab601-bbb2-4f64-9690-0bd246a73016", "name": "Дизайн"},
        {"id": "a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee", "name": "Веб-разработка"},
        {"id": "f52d35fc-52b8-48fd-8b60-74b6f5a68cd8", "name": "Мобильная разработка"},
        {"id": "ce5e11fd-f9c3-4a4d-8b4d-dc5e9b9a4c9d", "name": "Серверная разработка"},
        {"id": "f84e15be-2f74-4524-b02b-53bbd52e9e68", "name": "Искусственный интеллект"},
    ]

    task_categories = [TaskCategory(**data) for data in task_category_data]

    TaskCategory.objects.bulk_create(task_categories)


class Migration(migrations.Migration):
    dependencies = [
        ('Tasks', '0001_initial'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_task_categories),
    ]
