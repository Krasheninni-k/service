# Generated by Django 3.2.16 on 2023-09-07 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_customsettings_exchange_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='cash',
            field=models.BooleanField(default=False, verbose_name='Касса'),
        ),
    ]