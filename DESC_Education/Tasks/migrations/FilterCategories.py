from django.db import migrations
import requests
import csv


def get_filter_categories(apps, schema_editor):
    FilterCategory = apps.get_model('Tasks', 'FilterCategory')
    TaskCategory = apps.get_model('Tasks', 'TaskCategory')

    filter_category_data = [
        {"id": "0d504811-ae8c-47d3-acb8-7309ddcf5b3d", "name": "Языки программирования"},
        {"id": "b338787a-6286-4d69-ab93-e7ca5d0c3e7c", "name": "Уровни сложности"},
        {"id": "712c1bc8-41f6-4524-aeee-c36e91e7e36f", "name": "Виды заданий"},
        {"id": "b2b14635-3e06-445e-aa6a-db36f9dcbc0a", "name": "Формат заданий"},
    ]

    filter_categories = [FilterCategory(**data) for data in filter_category_data]

    FilterCategory.objects.bulk_create(filter_categories)

    for category in filter_categories:
        match category.name:
            case "Языки программирования":
                TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee").filter_categories.add(category)
                TaskCategory.objects.get(id="848254a3-bad2-4e0c-be20-bedce1700301").filter_categories.add(category)
                TaskCategory.objects.get(id="336eb2cb-a070-44d4-be55-dd1da7b683ad").filter_categories.add(category)
                TaskCategory.objects.get(id="46059fc9-2243-4968-bb50-7a8f3e231b50").filter_categories.add(category)

            case _:
                TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee").filter_categories.add(category)
                TaskCategory.objects.get(id="848254a3-bad2-4e0c-be20-bedce1700301").filter_categories.add(category)
                TaskCategory.objects.get(id="336eb2cb-a070-44d4-be55-dd1da7b683ad").filter_categories.add(category)
                TaskCategory.objects.get(id="46059fc9-2243-4968-bb50-7a8f3e231b50").filter_categories.add(category)
                TaskCategory.objects.get(id="bedab601-bbb2-4f64-9690-0bd246a73016").filter_categories.add(category)
                TaskCategory.objects.get(id="c8ce70d4-6d74-460e-935a-2ae229e633c9").filter_categories.add(category)



class Migration(migrations.Migration):
    dependencies = [
        ('Tasks', 'TaskCategories'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_filter_categories),
    ]
