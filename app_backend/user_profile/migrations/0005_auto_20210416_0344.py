# Generated by Django 3.1.5 on 2021-04-16 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0004_auto_20210403_0344'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='deviceToken',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='firebaseSub',
            field=models.TextField(default=''),
        ),
    ]
