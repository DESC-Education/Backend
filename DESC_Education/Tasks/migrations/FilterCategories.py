from django.db import migrations
import requests
import csv


def get_filter_categories(apps, schema_editor):
    FilterCategory = apps.get_model('Tasks', 'FilterCategory')
    TaskCategory = apps.get_model('Tasks', 'TaskCategory')

    filter_category_data = [
        {"name": "Языки программирования"},
        {"name": "Уровни сложности"},
        {"name": "Виды заданий"},
        {"name": "Формат заданий"},
    ]

    filter_categories = [FilterCategory(**data) for data in filter_category_data]

    FilterCategory.objects.bulk_create(filter_categories)

    for category in filter_categories:
        match category.name:
            case "Языки программирования":
                category.task_categories.add(TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee"))
                category.task_categories.add(TaskCategory.objects.get(id="848254a3-bad2-4e0c-be20-bedce1700301"))
                category.task_categories.add(TaskCategory.objects.get(id="336eb2cb-a070-44d4-be55-dd1da7b683ad"))
                category.task_categories.add(TaskCategory.objects.get(id="46059fc9-2243-4968-bb50-7a8f3e231b50"))
            case _:
                category.task_categories.add(TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee"))
                category.task_categories.add(TaskCategory.objects.get(id="848254a3-bad2-4e0c-be20-bedce1700301"))
                category.task_categories.add(TaskCategory.objects.get(id="336eb2cb-a070-44d4-be55-dd1da7b683ad"))
                category.task_categories.add(TaskCategory.objects.get(id="46059fc9-2243-4968-bb50-7a8f3e231b50"))
                category.task_categories.add(TaskCategory.objects.get(id="bedab601-bbb2-4f64-9690-0bd246a73016"))
                category.task_categories.add(TaskCategory.objects.get(id="c8ce70d4-6d74-460e-935a-2ae229e633c9"))


class Migration(migrations.Migration):
    dependencies = [
        ('Tasks', 'TaskCategories'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_filter_categories),
    ]
