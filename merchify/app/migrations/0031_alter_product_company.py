# Generated by Django 4.2.16 on 2024-11-09 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_alter_product_artist_alter_product_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='app.company'),
        ),
    ]
