# Generated by Django 4.2.3 on 2024-03-08 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0029_vacancy_last_updated_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='vacancy_type',
            field=models.CharField(choices=[('Internal', 'Internal'), ('Careers', 'Career'), ('Internship', 'Internship'), ('Attachment', 'Attachment')], max_length=20),
        ),
    ]
