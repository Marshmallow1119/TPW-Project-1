# Generated by Django 4.2.11 on 2024-11-08 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_cartitem_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
