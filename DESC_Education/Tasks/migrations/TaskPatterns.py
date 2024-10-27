from django.db import migrations
import requests
import csv


def get_task_patterns(apps, schema_editor):
    TaskPattern = apps.get_model('Tasks', 'TaskPattern')

    task_pattern_data = [
        {"title": "Лендинг",
         "description": "Сверстать лендинг для рекламы компании",
         "category_id": "a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee"
        },
        {"title": "Нейронная сеть",
         "description": "Создать и обучить нейронную сеть для следующей задачи:",
         "category_id": "f84e15be-2f74-4524-b02b-53bbd52e9e68"
         },
        {"title": "Сервер для простых CRUD-ов",
         "description": "Создать сервер для простых CRUD-ов для следующей задачи:",
         "category_id": "ce5e11fd-f9c3-4a4d-8b4d-dc5e9b9a4c9d"
         },
    ]

    task_patterns = [TaskPattern(**data) for data in task_pattern_data]

    TaskPattern.objects.bulk_create(task_patterns)

    Filter = apps.get_model('Tasks', 'Filter')
    # for task_pattern in task_patterns:
    #     if task_pattern.title == "Лендинг":
    #         task_pattern.filters.add(Filter.objects.get(name="Начинающий"))
    #         task_pattern.filters.add(Filter.objects.get(name="Кейсы"))
    #     elif task_pattern.title == "Нейронная сеть":
    #         task_pattern.filters.add(Filter.objects.get(name="Продвинутый"))
    #         task_pattern.filters.add(Filter.objects.get(name="Python"))
    #     elif task_pattern.title == "Сервер для простых CRUD-ов":
    #         task_pattern.filters.add(Filter.objects.get(name="Python"))
    #         task_pattern.filters.add(Filter.objects.get(name="Начинающий"))
    #         task_pattern.filters.add(Filter.objects.get(name="Cредний"))




class Migration(migrations.Migration):
    dependencies = [
        ('Tasks', 'Filters'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_task_patterns),
    ]
