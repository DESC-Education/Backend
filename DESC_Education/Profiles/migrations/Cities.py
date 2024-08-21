from django.db import migrations
import requests
from Settings.env_config import config
import csv


def get_cities(apps, schema_editor):
    City = apps.get_model('Profiles', 'City')

    cities_data = []
    city_names = set()
    with open('Profiles/migrations/cities.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            name = row[0]
            region = row[1]
            if name in city_names:
                continue
            city_names.add(name)
            cities_data.append({"name": name, "region": region})

    cities = [City(**data) for data in cities_data]

    City.objects.bulk_create(cities)


class Migration(migrations.Migration):
    dependencies = [
        ('Profiles', '0001_initial'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_cities),
    ]
