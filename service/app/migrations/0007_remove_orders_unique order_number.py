# Generated by Django 3.2.16 on 2023-10-23 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_sales_cash'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='orders',
            name='Unique order_number',
        ),
    ]
