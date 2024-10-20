# Generated by Django 4.2.16 on 2024-10-13 09:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0012_alter_goods_received'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='received_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата приемки'),
        ),
        migrations.CreateModel(
            name='Scan_sn_number',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('is_published', models.BooleanField(default=True, verbose_name='Опубликовано')),
                ('sn_number', models.CharField(max_length=256, verbose_name='S/n номер')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор записи')),
            ],
            options={
                'verbose_name': 'S/n номер',
                'verbose_name_plural': 'S/n номера',
            },
        ),
    ]