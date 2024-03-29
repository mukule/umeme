# Generated by Django 4.2.3 on 2023-09-27 11:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_certificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='access_level',
            field=models.PositiveIntegerField(choices=[(1, 'System Admin'), (2, 'HR'), (3, 'HR Interns'), (4, 'HR Attachments')], default=0),
        ),
        migrations.CreateModel(
            name='UserAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
