# Generated by Django 3.1.4 on 2022-06-15 07:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flourish_reports', '0002_recruitmentreport'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecruitmentReport',
            new_name='RecruitmentStats',
        ),
    ]
