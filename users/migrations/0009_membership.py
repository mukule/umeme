# Generated by Django 4.2.3 on 2023-08-16 08:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_certification_certificate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membership_title', models.CharField(blank=True, max_length=255, null=True)),
                ('membership_number', models.CharField(blank=True, max_length=50, null=True)),
                ('date_joined', models.DateField(blank=True, null=True)),
                ('membership_certificate', models.FileField(blank=True, null=True, upload_to='memberships/')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
