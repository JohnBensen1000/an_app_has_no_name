# Generated by Django 3.1.5 on 2021-02-20 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_profile', '0002_auto_20210212_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='postprofile',
            name='video',
            field=models.BooleanField(default=False),
        ),
    ]