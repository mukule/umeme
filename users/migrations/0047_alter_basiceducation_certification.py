# Generated by Django 4.2.4 on 2024-01-19 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0046_remove_basiceducation_index_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basiceducation',
            name='certification',
            field=models.CharField(blank=True, choices=[('KCSE', 'Kenya Certificate of Secondary Education (KCSE)')], default='kcse', max_length=10, null=True),
        ),
    ]
