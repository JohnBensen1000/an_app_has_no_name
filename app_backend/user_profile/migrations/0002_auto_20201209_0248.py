# Generated by Django 3.1.4 on 2020-12-09 02:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationships',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creators', to='user_profile.userprofile'),
        ),
        migrations.AlterField(
            model_name='relationships',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='user_profile.userprofile'),
        ),
    ]
