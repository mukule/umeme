# Generated by Django 4.2.3 on 2023-08-21 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_alter_customuser_access_level'),
        ('vacancies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='min_educational_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.educationallevel'),
        ),
    ]
