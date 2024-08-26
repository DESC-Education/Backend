from django.db import migrations
import requests
from Settings.env_config import config
import csv

def get_skills(apps, schema_editor):
    Skill = apps.get_model('Profiles', 'Skill')

    skills_data = []

    with open('Profiles/migrations/skills.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            id = row[0]
            name = row[1]
            skills_data.append({"id": id, "name": name})



    skills = [Skill(**data) for data in skills_data]

    Skill.objects.bulk_create(skills)



class Migration(migrations.Migration):

    dependencies = [
        ('Profiles', 'Universities'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_skills),
    ]