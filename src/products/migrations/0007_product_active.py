# Generated by Django 3.2 on 2021-04-29 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_rename_feature_product_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
