# Generated by Django 4.2.16 on 2024-10-13 09:47

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0013_alter_goods_received_date_scan_sn_number'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Scan_sn_number',
            new_name='ScanSnNumber',
        ),
    ]
