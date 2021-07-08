# Generated by Django 3.2.4 on 2021-06-20 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0021_auto_20210620_1901'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='blocked',
        ),
        migrations.AddField(
            model_name='user',
            name='allRelationships',
            field=models.ManyToManyField(through='models.Relationships', to='models.User'),
        ),
        migrations.AlterField(
            model_name='relationships',
            name='relation',
            field=models.IntegerField(choices=[(0, 'Following'), (1, 'Blocked')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='profileColor',
            field=models.CharField(default='blue', max_length=10),
        ),
        migrations.DeleteModel(
            name='Blocked',
        ),
    ]