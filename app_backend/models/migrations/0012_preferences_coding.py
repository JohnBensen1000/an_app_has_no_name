# Generated by Django 3.2.4 on 2021-06-09 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0011_preferences_gaming'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferences',
            name='coding',
            field=models.FloatField(default=0.1),
        ),
    ]
