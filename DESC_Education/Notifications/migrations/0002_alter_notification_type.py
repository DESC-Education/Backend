# Generated by Django 5.0.7 on 2024-10-27 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('verification', 'Verification'), ('evaluation', 'Evaluation'), ('level', 'Level'), ('review', 'Review'), ('countReset', 'Count Reset'), ('solution', 'Solution'), ('viewed', 'viewed')], max_length=20),
        ),
    ]
