# Generated by Django 4.2.4 on 2024-01-20 14:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vacancies', '0026_alter_useracceptedterms_terms'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useracceptedterms',
            name='terms',
        ),
        migrations.AlterField(
            model_name='useracceptedterms',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]