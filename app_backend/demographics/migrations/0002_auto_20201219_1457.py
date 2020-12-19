# Generated by Django 3.1.4 on 2020-12-19 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demographics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demographics',
            name='art',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='comedy',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='dance',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='female',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='lifestyle',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='male',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='other',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='selfhelp',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='skits',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='sports',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y0_12',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y13_18',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y19_24',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y25_29',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y30_34',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y35_39',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y40_49',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y50_59',
            field=models.FloatField(default=0.1),
        ),
        migrations.AddField(
            model_name='demographics',
            name='y60_up',
            field=models.FloatField(default=0.1),
        ),
    ]
