# Generated by Django 3.2.4 on 2021-07-24 18:09

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0034_alter_chat_lastchattime'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmember',
            name='newChats',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chat',
            name='lastChatTime',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 24, 18, 9, 16, 93538, tzinfo=utc)),
        ),
    ]
