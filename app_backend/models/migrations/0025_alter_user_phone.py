# Generated by Django 3.2.4 on 2021-07-02 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0024_auto_20210621_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(default='', max_length=15),
        ),
    ]
