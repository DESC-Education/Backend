from django.db import migrations
import requests
from Settings.env_config import config


def get_skills(apps, schema_editor):
    Skill = apps.get_model('Profiles', 'Skill')

    skills_data = [
        {'name': "Python"},
        {'name': "C#"},
        {'name': "C++"},
        {'name': "Photoshop"},
        {'name': "Figma"},
        {'name': "Adobe Illustrator"},
        {'name': "Анимация"},
    ]

    skills = [Skill(**data) for data in skills_data]

    Skill.objects.bulk_create(skills)



class Migration(migrations.Migration):

    dependencies = [
        ('Profiles', 'Universities'),  # Замените на имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(get_skills),
    ]