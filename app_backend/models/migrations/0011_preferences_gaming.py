# Generated by Django 3.2.4 on 2021-06-09 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0010_preferences_outdoors'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferences',
            name='gaming',
            field=models.FloatField(default=0.1),
        ),
    ]