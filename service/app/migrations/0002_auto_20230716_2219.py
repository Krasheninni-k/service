# Generated by Django 3.2.16 on 2023-07-16 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales',
            name='client_contact',
            field=models.CharField(blank=True, default='Нет данных', max_length=256, null=True, verbose_name='Контакт'),
        ),
        migrations.AddField(
            model_name='sales',
            name='regular_client',
            field=models.BooleanField(default=False, verbose_name='Повторное обращение'),
        ),
    ]
