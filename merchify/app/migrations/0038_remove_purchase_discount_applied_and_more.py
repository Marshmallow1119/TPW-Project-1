# Generated by Django 4.2.16 on 2024-11-09 23:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_merge_20241109_2328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='discount_applied',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='discount_value',
        ),
    ]
