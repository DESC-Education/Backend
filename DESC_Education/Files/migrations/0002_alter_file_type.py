# Generated by Django 5.0.7 on 2024-09-27 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Files', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='type',
            field=models.CharField(choices=[('verification_file', 'Файлы верификации'), ('task_file', 'Файлы задач'), ('solution_file', 'Файлы решений'), ('chat_file', 'Файлы чатов')], max_length=20),
        ),
    ]
