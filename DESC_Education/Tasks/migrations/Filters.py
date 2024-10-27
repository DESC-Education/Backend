from django.db import migrations
import requests
import csv


def get_filters(apps, schema_editor):
    Filter = apps.get_model('Tasks', 'Filter')

    filter_data = [
        {"name": "Cредний", "filter_category_id": "13ab5b9b-b94c-4fce-aeb7-7b8752f1d4dd"},
        {"name": "Начинающий", "filter_category_id": "13ab5b9b-b94c-4fce-aeb7-7b8752f1d4dd"},
        {"name": "Продвинутый", "filter_category_id": "13ab5b9b-b94c-4fce-aeb7-7b8752f1d4dd"},

        {"name": "Игра", "filter_category_id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5"},
        {"name": "Сайт", "filter_category_id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5"},
        {"name": "Мобильное приложение", "filter_category_id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5"},
        {"name": "Анимационное видео", "filter_category_id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5"},

        {"name": "Blender", "filter_category_id": "07db122e-c89a-43b8-b60e-f2faf7ce665e"},
        {"name": "Adobe", "filter_category_id": "07db122e-c89a-43b8-b60e-f2faf7ce665e"},
        {"name": "Unreal Engine", "filter_category_id": "07db122e-c89a-43b8-b60e-f2faf7ce665e"},
        {"name": "Unity", "filter_category_id": "07db122e-c89a-43b8-b60e-f2faf7ce665e"},

        {"name": "2D", "filter_category_id": "a252a1a7-021e-4edc-97f7-58a3b65ba4ab"},
        {"name": "3D", "filter_category_id": "a252a1a7-021e-4edc-97f7-58a3b65ba4ab"},
        {"name": "Моушн-дизайн", "filter_category_id": "a252a1a7-021e-4edc-97f7-58a3b65ba4ab"},

        {"name": "Сайт / Мобильное приложение", "filter_category_id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5"},
        {"name": "Одежда", "filter_category_id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5"},
        {"name": "Арты", "filter_category_id": "46ee9811-8aae-44a3-b5b2-09f6287b59f5"},

        {"name": "Photoshop", "filter_category_id": "f922e3dc-7d14-4914-8528-17d5a84a33de"},
        {"name": "Figma", "filter_category_id": "f922e3dc-7d14-4914-8528-17d5a84a33de"},
        {"name": "Adobe Illustrator", "filter_category_id": "f922e3dc-7d14-4914-8528-17d5a84a33de"},
        {"name": "Другое", "filter_category_id": "f922e3dc-7d14-4914-8528-17d5a84a33de"},

        {"name": "UI/UX дизайн", "filter_category_id": "d18c1c5a-2d58-4c5c-aff5-d9c9a88be56d"},
        {"name": "Графический дизайн", "filter_category_id": "d18c1c5a-2d58-4c5c-aff5-d9c9a88be56d"},
        {"name": "Дизайн интерьера", "filter_category_id": "d18c1c5a-2d58-4c5c-aff5-d9c9a88be56d"},

        {"name": "HTML + CSS + JS", "filter_category_id": "e2e4ae39-a24a-4df0-98bd-075e2e4caef9"},
        {"name": "ReactJS", "filter_category_id": "e2e4ae39-a24a-4df0-98bd-075e2e4caef9"},
        {"name": "VueJS Illustrator", "filter_category_id": "e2e4ae39-a24a-4df0-98bd-075e2e4caef9"},
        {"name": "Angular", "filter_category_id": "e2e4ae39-a24a-4df0-98bd-075e2e4caef9"},

        {"name": "Статический", "filter_category_id": "06f75405-7593-4fe0-a984-f6f56c224e93"},
        {"name": "Динамический", "filter_category_id": "06f75405-7593-4fe0-a984-f6f56c224e93"},

        {"name": "Не требуется", "filter_category_id": "e79d1594-b3f0-4038-b1f4-b7dfb68a6f64"},
        {"name": "Базовая", "filter_category_id": "e79d1594-b3f0-4038-b1f4-b7dfb68a6f64"},
        {"name": "Продвинутая", "filter_category_id": "e79d1594-b3f0-4038-b1f4-b7dfb68a6f64"},

        {"name": "Android", "filter_category_id": "c22ec442-134e-4557-a763-fac78e747220"},
        {"name": "iOS", "filter_category_id": "c22ec442-134e-4557-a763-fac78e747220"},
        {"name": "Кроссплатформенная", "filter_category_id": "c22ec442-134e-4557-a763-fac78e747220"},

        {"name": "Kotlin", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "Swift", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "Flutter (Dart)", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "JavaScript", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "Python", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "Java", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "PHP", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "Ruby", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "Go", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},
        {"name": "Rust", "filter_category_id": "db6f4f5f-e17a-422e-bb20-6e82f0913f3e"},



        {"name": "React Native", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Flutter", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Xamarin", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Cordova", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Express.js", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Django", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Laravel", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Rails", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},
        {"name": "Spring", "filter_category_id": "db38f4f3-7647-4923-b6f4-87b7933187dc"},

        {"name": "Машинное обучение", "filter_category_id": "3bdac9da-a7d7-4be4-bb5d-dadebfa1f00f"},
        {"name": "Нейронные сети", "filter_category_id": "3bdac9da-a7d7-4be4-bb5d-dadebfa1f00f"},
        {"name": "Глубокое обучение", "filter_category_id": "3bdac9da-a7d7-4be4-bb5d-dadebfa1f00f"},

        {"name": "TensorFlow", "filter_category_id": "8c9b5bed-e73f-46fa-af66-153041ed8b2d"},
        {"name": "PyTorch", "filter_category_id": "8c9b5bed-e73f-46fa-af66-153041ed8b2d"},
        {"name": "Keras", "filter_category_id": "8c9b5bed-e73f-46fa-af66-153041ed8b2d"},






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
