# Generated by Django 4.2.4 on 2024-03-09 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0033_alter_jobtype_banner_alter_jobtype_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobtype',
            name='icon',
            field=models.ImageField(blank=True, default='default/icon.png', null=True, upload_to='job_type_icons/'),
        ),
    ]
