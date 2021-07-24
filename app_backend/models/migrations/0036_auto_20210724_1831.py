# Generated by Django 3.2.4 on 2021-07-24 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0035_auto_20210724_1809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmember',
            name='newChats',
        ),
        migrations.AddField(
            model_name='chatmember',
            name='isUpdated',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='chat',
            name='lastChatTime',
            field=models.DateTimeField(),
        ),
    ]
