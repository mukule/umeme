# Generated by Django 4.2.6 on 2023-10-25 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_staff_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='access_level',
            field=models.PositiveIntegerField(choices=[(0, 'registrants'), (1, 'System Admin'), (2, 'HR'), (3, 'HR Interns'), (4, 'HR Attachments'), (5, 'staffs')], default=0),
        ),
    ]
