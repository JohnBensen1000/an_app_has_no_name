# Generated by Django 3.1.5 on 2021-05-26 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='private',
            new_name='isPrivate',
        ),
        migrations.AlterField(
            model_name='post',
            name='postID',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
