# Generated by Django 3.1.4 on 2023-01-26 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flourish_reports', '0009_pietotalstats'),
    ]

    operations = [
        migrations.AddField(
            model_name='recruitmentstats',
            name='offstudy',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Offstudy'),
        ),
    ]
