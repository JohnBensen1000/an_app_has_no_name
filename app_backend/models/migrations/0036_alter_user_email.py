# Generated by Django 3.2.4 on 2022-02-13 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0035_remove_user_isappupdated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=50),
        ),
    ]
