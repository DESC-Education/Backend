from django.db import migrations
import requests
from Settings.env_config import config


def get_skills(apps, schema_editor):
    Skill = apps.get_model('Profiles', 'Skill')

    skills_data = [
        {'name': "Python", 'is_verified': True},
        {'name': "C#", 'is_verified': True},
        {'name': "C++", 'is_verified': True},
        {'name': "Photoshop", 'is_verified': True},
        {'name': "Figma", 'is_verified': True},
        {'name': "Adobe Illustrator", 'is_verified': True},
        {'name': "Анимация", 'is_verified': True},
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