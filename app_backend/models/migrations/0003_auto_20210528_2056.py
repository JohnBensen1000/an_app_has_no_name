# Generated by Django 3.1.5 on 2021-05-28 20:56

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0002_auto_20210528_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmember',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.chat'),
        ),
        migrations.AlterField(
            model_name='post',
            name='timeCreated',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 28, 20, 56, 27, 963203, tzinfo=utc)),
        ),
    ]