# Generated by Django 3.2.4 on 2021-07-28 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='isUpdated',
            field=models.BooleanField(default=True),
        ),
    ]
