from django.db import migrations
import requests
import csv


def get_task_categories(apps, schema_editor):
    TaskCategory = apps.get_model('Tasks', 'TaskCategory')

    task_category_data = [
        {"id": "a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee", "name": "Веб-разработка"},
        {"id": "848254a3-bad2-4e0c-be20-bedce1700301", "name": "Мобильная разработка"},
        {"id": "336eb2cb-a070-44d4-be55-dd1da7b683ad", "name": "Искусственный интеллект"},
        {"id": "46059fc9-2243-4968-bb50-7a8f3e231b50", "name": "Базы данных"},
        {"id": "bedab601-bbb2-4f64-9690-0bd246a73016", "name": "Дизайн"},
        {"id": "c8ce70d4-6d74-460e-935a-2ae229e633c9", "name": "Анимация"},
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
