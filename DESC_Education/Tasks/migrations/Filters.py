from django.db import migrations
import requests
import csv


def get_filters(apps, schema_editor):
    Filter = apps.get_model('Tasks', 'Filter')

    filter_data = [
        {"name": "Python", "filter_category_id": "0d504811-ae8c-47d3-acb8-7309ddcf5b3d"},
        {"name": "C#", "filter_category_id": "0d504811-ae8c-47d3-acb8-7309ddcf5b3d"},
        {"name": "Начинающий", "filter_category_id": "b338787a-6286-4d69-ab93-e7ca5d0c3e7c"},
        {"name": "Cредний", "filter_category_id": "b338787a-6286-4d69-ab93-e7ca5d0c3e7c"},
        {"name": "Продвинутый", "filter_category_id": "b338787a-6286-4d69-ab93-e7ca5d0c3e7c"},
        {"name": "Программирование", "filter_category_id": "712c1bc8-41f6-4524-aeee-c36e91e7e36f"},
        {"name": "Тестирование", "filter_category_id": "712c1bc8-41f6-4524-aeee-c36e91e7e36f"},
        {"name": "Проектирование", "filter_category_id": "712c1bc8-41f6-4524-aeee-c36e91e7e36f"},
        {"name": "Проекты", "filter_category_id": "b2b14635-3e06-445e-aa6a-db36f9dcbc0a"},
        {"name": "Кейсы", "filter_category_id": "b2b14635-3e06-445e-aa6a-db36f9dcbc0a"},
        {"name": "Тесты", "filter_category_id": "b2b14635-3e06-445e-aa6a-db36f9dcbc0a"},
        {"name": "Задачи", "filter_category_id": "b2b14635-3e06-445e-aa6a-db36f9dcbc0a"},
    ]

    filters = [Filter(**data) for data in filter_data]

    Filter.objects.bulk_create(filters)


class Migration(migrations.Migration):
    dependencies = [
        ('Tasks', 'FilterCategories'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_filters),
    ]
