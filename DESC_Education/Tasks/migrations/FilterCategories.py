from django.db import migrations
import requests
import csv


def get_filter_categories(apps, schema_editor):
    FilterCategory = apps.get_model('Tasks', 'FilterCategory')
    TaskCategory = apps.get_model('Tasks', 'TaskCategory')

    filter_category_data = [
        {"id": "13ab5b9b-b94c-4fce-aeb7-7b8752f1d4dd", "name": "Уровни сложности"},
        {"id": "07db122e-c89a-43b8-b60e-f2faf7ce665e", "name": "Инструментарий"},
        {"id": "8c9b5bed-e73f-46fa-af66-153041ed8b2d", "name": "Библиотеки"},
        {"id": "e2e4ae39-a24a-4df0-98bd-075e2e4caef9", "name": "Технология"},
        {"id": "db38f4f3-7647-4923-b6f4-87b7933187dc", "name": "Фреймворки"},
        {"id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e", "name": "Языки программирования"},
        {"id": "e79d1594-b3f0-4038-b1f4-b7dfb68a6f64", "name": "SEO-оптимизация"},
        {"id": "d18c1c5a-2d58-4c5c-aff5-d9c9a88be56d", "name": "Тип дизайна"},
        {"id": "3bdac9da-a7d7-4be4-bb5d-dadebfa1f00f", "name": "Подразделы"},
        {"id": "06f75405-7593-4fe0-a984-f6f56c224e93", "name": "Вид контента"},
        {"id": "c22ec442-134e-4557-a763-fac78e747220", "name": "Операционная система"},
        {"id": "f922e3dc-7d14-4914-8528-17d5a84a33de", "name": "Рабочее пространство"},
        {"id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5", "name": "Назначение"},
        {"id": "a252a1a7-021e-4edc-97f7-58a3b65ba4ab", "name": "Тип анимации"},
    ]

    filter_categories = [FilterCategory(**data) for data in filter_category_data]

    FilterCategory.objects.bulk_create(filter_categories)

    for category in filter_categories:
        match category.name:
            case "Уровни сложности":
                TaskCategory.objects.get(id="c8ce70d4-6d74-460e-935a-2ae229e633c9").filter_categories.add(category)
                TaskCategory.objects.get(id="bedab601-bbb2-4f64-9690-0bd246a73016").filter_categories.add(category)
                TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee").filter_categories.add(category)
                TaskCategory.objects.get(id="f52d35fc-52b8-48fd-8b60-74b6f5a68cd8").filter_categories.add(category)
                TaskCategory.objects.get(id="ce5e11fd-f9c3-4a4d-8b4d-dc5e9b9a4c9d").filter_categories.add(category)
                TaskCategory.objects.get(id="f84e15be-2f74-4524-b02b-53bbd52e9e68").filter_categories.add(category)

            case 'Назначение':
                TaskCategory.objects.get(id="c8ce70d4-6d74-460e-935a-2ae229e633c9").filter_categories.add(category)
                TaskCategory.objects.get(id="bedab601-bbb2-4f64-9690-0bd246a73016").filter_categories.add(category)

            case 'Инструментарий':
                TaskCategory.objects.get(id="c8ce70d4-6d74-460e-935a-2ae229e633c9").filter_categories.add(category)

            case 'Тип анимации':
                TaskCategory.objects.get(id="c8ce70d4-6d74-460e-935a-2ae229e633c9").filter_categories.add(category)

            case 'Рабочее пространство':
                TaskCategory.objects.get(id="bedab601-bbb2-4f64-9690-0bd246a73016").filter_categories.add(category)

            case 'Тип дизайна':
                TaskCategory.objects.get(id="bedab601-bbb2-4f64-9690-0bd246a73016").filter_categories.add(category)


            case 'Технология':
                TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee").filter_categories.add(category)


            case 'Вид контента':
                TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee").filter_categories.add(category)
            case 'SEO-оптимизация':
                TaskCategory.objects.get(id="a7ab9087-ec21-4b7c-9f2a-c6158e8d52ee").filter_categories.add(category)
            case 'Операционная система':
                TaskCategory.objects.get(id="f52d35fc-52b8-48fd-8b60-74b6f5a68cd8").filter_categories.add(category)
            case 'Языки программирования':
                TaskCategory.objects.get(id="f52d35fc-52b8-48fd-8b60-74b6f5a68cd8").filter_categories.add(category)
                TaskCategory.objects.get(id="ce5e11fd-f9c3-4a4d-8b4d-dc5e9b9a4c9d").filter_categories.add(category)
                TaskCategory.objects.get(id="f84e15be-2f74-4524-b02b-53bbd52e9e68").filter_categories.add(category)


            case 'Фреймворки':
                TaskCategory.objects.get(id="f52d35fc-52b8-48fd-8b60-74b6f5a68cd8").filter_categories.add(category)
                TaskCategory.objects.get(id="ce5e11fd-f9c3-4a4d-8b4d-dc5e9b9a4c9d").filter_categories.add(category)

            case 'Подразделы':
                TaskCategory.objects.get(id="f84e15be-2f74-4524-b02b-53bbd52e9e68").filter_categories.add(category)

            case 'Библиотеки':
                TaskCategory.objects.get(id="f84e15be-2f74-4524-b02b-53bbd52e9e68").filter_categories.add(category)










class Migration(migrations.Migration):
    dependencies = [
        ('Tasks', 'TaskCategories'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_filter_categories),
    ]
