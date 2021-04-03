# Generated by Django 3.1.5 on 2021-04-02 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountinfo',
            name='profilePicStatus',
            field=models.IntegerField(choices=[(0, 'No profile pic'), (1, 'Profile pic is image'), (2, 'Profile pic is video')], default=0),
        ),
    ]