# Generated by Django 4.2.4 on 2024-03-09 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0034_alter_jobtype_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobtype',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
