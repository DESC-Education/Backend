from django.db import migrations
import requests
from Settings.env_config import config


def get_universities(apps, schema_editor):
    University = apps.get_model('Profiles', 'University')

    raw_universities = requests.get("https://api.socio.center/public/priority/list").json()

    universities_list = raw_universities.get('data').get('participants')

    universities_data = []

    for i in universities_list:
        name = i.get("name").replace(
            'Федеральное государственное автономное образовательное учреждение высшего образования',
            "ФГАОУ ВО").replace('Федеральное государственное бюджетное образовательное учреждение высшего образования',
                                "ФГБОУ ВО").replace(
            'федеральное государственное бюджетное образовательное учреждение высшего образования',
            "ФГБОУ ВО").replace('федеральное государственное автономное образовательное учреждение высшего образования',
                                "ФГАОУ ВО")
        short_name = i.get('shortName')


        universities_data.append({"name": name, "short_name": short_name})

    universities = [University(**data) for data in universities_data]

    University.objects.bulk_create(universities)



class Migration(migrations.Migration):

    dependencies = [
        ('Profiles', 'Cities'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_universities),
    ]