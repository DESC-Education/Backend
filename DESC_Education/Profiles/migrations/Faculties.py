from django.db import migrations
import requests
from Settings.env_config import config
import csv


def get_faculties(apps, schema_editor):
    Faculty = apps.get_model('Profiles', 'Faculty')

    faculties_data = []

    with open('Profiles/migrations/faculties.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            id = row[0]
            name = row[1]
            university_id = row[2]
            faculties_data.append({"id": id, "name": name, "university_id": university_id})


    faculties = [Faculty(**data) for data in faculties_data]

    Faculty.objects.bulk_create(faculties)


class Migration(migrations.Migration):
    dependencies = [
        ('Profiles', 'Skills'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_faculties),
    ]
