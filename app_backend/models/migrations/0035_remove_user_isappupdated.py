# Generated by Django 3.2.4 on 2021-08-04 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0034_user_isappupdated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='isAppUpdated',
        ),
    ]
