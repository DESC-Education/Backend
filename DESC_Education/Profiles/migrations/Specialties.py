from django.db import migrations
import requests
from Settings.env_config import config
import csv


def get_specialities(apps, schema_editor):
    Specialty = apps.get_model('Profiles', 'Specialty')

    specialities_data = []

    with open('Profiles/migrations/specialties.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            code = row[0]
            name = row[1]
            type = row[2]

            specialities_data.append({"code": code, "name": name, "type": type})

    specialities = [Specialty(**data) for data in specialities_data]


    Specialty.objects.bulk_create(specialities)


class Migration(migrations.Migration):
    dependencies = [
        ('Profiles', 'Faculties'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_specialities),
    ]
