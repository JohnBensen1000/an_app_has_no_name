# Generated by Django 3.2.4 on 2021-06-21 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0023_blocked'),
    ]

    operations = [
        migrations.CreateModel(
            name='Following',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('newFollower', models.BooleanField(default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='allRelationships',
        ),
        migrations.DeleteModel(
            name='Relationships',
        ),
        migrations.AddField(
            model_name='following',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='models.user'),
        ),
        migrations.AddField(
            model_name='following',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followings', to='models.user'),
        ),
    ]
