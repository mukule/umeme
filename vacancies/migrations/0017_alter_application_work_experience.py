# Generated by Django 4.2.6 on 2023-10-23 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0016_vacancy_college_required_alter_vacancy_vacancy_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='work_experience',
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]
