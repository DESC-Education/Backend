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
         "category_id": "336eb2cb-a070-44d4-be55-dd1da7b683ad"
         },
        {"title": "Сервер для простых CRUD-ов",
         "description": "Создать сервер для простых CRUD-ов для следующей задачи:",
         "category_id": "46059fc9-2243-4968-bb50-7a8f3e231b50"
         },
    ]

    task_patterns = [TaskPattern(**data) for data in task_pattern_data]

    TaskPattern.objects.bulk_create(task_patterns)

    Filter = apps.get_model('Tasks', 'Filter')
    for task_pattern in task_patterns:
        if task_pattern.title == "Лендинг":
            task_pattern.filters.add(Filter.objects.get(name="Начинающий"))
            task_pattern.filters.add(Filter.objects.get(name="Кейсы"))
        elif task_pattern.title == "Нейронная сеть":
            task_pattern.filters.add(Filter.objects.get(name="Продвинутый"))
            task_pattern.filters.add(Filter.objects.get(name="Python"))
        elif task_pattern.title == "Сервер для простых CRUD-ов":
            task_pattern.filters.add(Filter.objects.get(name="Python"))
            task_pattern.filters.add(Filter.objects.get(name="Начинающий"))
            task_pattern.filters.add(Filter.objects.get(name="Cредний"))




class Migration(migrations.Migration):
    dependencies = [
        ('Tasks', 'Filters'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_task_patterns),
    ]
