# Generated by Django 4.2.16 on 2024-10-13 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_rename_scan_sn_number_scansnnumber'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scansnnumber',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='scansnnumber',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='scansnnumber',
            name='is_published',
        ),
    ]
