# Generated by Django 3.2.4 on 2021-06-17 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0017_auto_20210617_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='downloadURL',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='profile',
            name='downloadURL',
            field=models.TextField(default=''),
        ),
    ]
