from django.db import migrations
import requests
from Settings.env_config import config
import csv

def get_universities(apps, schema_editor):
    University = apps.get_model('Profiles', 'University')
    universities_data = []


    with open('Profiles/migrations/universities.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            id = row[4]
            name = row[1]
            city_id = row[3]

            universities_data.append({'id': id, "name": name, "city_id": city_id})

    universities = [University(**data) for data in universities_data]

    University.objects.bulk_create(universities)



class Migration(migrations.Migration):

    dependencies = [
        ('Profiles', 'Cities'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_universities),
    ]