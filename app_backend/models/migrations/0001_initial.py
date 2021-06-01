# Generated by Django 3.1.5 on 2021-05-28 20:38

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chatID', models.CharField(max_length=50, unique=True)),
                ('chatName', models.CharField(default='', max_length=50)),
                ('isDirectMessage', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('male', models.FloatField(default=0.1)),
                ('female', models.FloatField(default=0.1)),
                ('other', models.FloatField(default=0.1)),
                ('y0_12', models.FloatField(default=0.1)),
                ('y13_18', models.FloatField(default=0.1)),
                ('y19_24', models.FloatField(default=0.1)),
                ('y25_29', models.FloatField(default=0.1)),
                ('y30_34', models.FloatField(default=0.1)),
                ('y35_39', models.FloatField(default=0.1)),
                ('y40_49', models.FloatField(default=0.1)),
                ('y50_59', models.FloatField(default=0.1)),
                ('y60_up', models.FloatField(default=0.1)),
                ('sports', models.FloatField(default=0.1)),
                ('dance', models.FloatField(default=0.1)),
                ('comedy', models.FloatField(default=0.1)),
                ('skits', models.FloatField(default=0.1)),
                ('lifestyle', models.FloatField(default=0.1)),
                ('art', models.FloatField(default=0.1)),
                ('selfHelp', models.FloatField(default=0.1)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exists', models.BooleanField(default=False)),
                ('isImage', models.BooleanField(default=True)),
                ('downloadURL', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Relationships',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relation', models.IntegerField(choices=[(0, 'Following'), (1, 'Blocked')], default=0)),
                ('newFollower', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.CharField(max_length=50, unique=True)),
                ('email', models.CharField(max_length=50, unique=True)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('uid', models.CharField(max_length=15, unique=True)),
                ('deviceToken', models.TextField(default='')),
                ('username', models.CharField(default='', max_length=20)),
                ('preferredLanguage', models.CharField(default='', max_length=20)),
                ('signedIn', models.BooleanField(default=False)),
                ('allRelationships', models.ManyToManyField(through='models.Relationships', to='models.User')),
                ('preferences', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='models.preferences')),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='models.profile')),
            ],
        ),
        migrations.AddField(
            model_name='relationships',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='models.user'),
        ),
        migrations.AddField(
            model_name='relationships',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followings', to='models.user'),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('postID', models.FloatField(primary_key=True, serialize=False)),
                ('isPrivate', models.BooleanField(default=False)),
                ('isImage', models.BooleanField()),
                ('timeCreated', models.DateTimeField(default=datetime.datetime(2021, 5, 28, 20, 38, 10, 358901, tzinfo=utc))),
                ('downloadURL', models.CharField(max_length=75)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created', to='models.user')),
                ('preferences', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='models.preferences')),
                ('watchedBy', models.ManyToManyField(related_name='watched', to='models.User')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isOwner', models.BooleanField(default=False)),
                ('chat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='models.chat')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='models.user')),
            ],
        ),
    ]