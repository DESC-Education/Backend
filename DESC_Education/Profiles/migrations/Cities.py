from django.db import migrations
import requests
from Settings.env_config import config


def get_cities(apps, schema_editor):
    City = apps.get_model('Profiles', 'City')

    res = requests.get("https://raw.githubusercontent.com/epogrebnyak/ru-cities/main/assets/towns.csv").text

    raw_cities = res.split('\n')[1:-1]
    city_names = set()
    cities_data = []

    for city in raw_cities:
        city = city.split(',')
        city_name = city[0]

        if city_name not in city_names:
            city_names.add(city_name)
            cities_data.append({"name": city_name, "region": city[4]})

    cities = [City(**data) for data in cities_data]

    City.objects.bulk_create(cities)



class Migration(migrations.Migration):

    dependencies = [
        ('Profiles', '0001_initial'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_cities),
    ]