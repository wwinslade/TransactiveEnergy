# Generated by Django 4.2.18 on 2025-04-01 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0007_device_adr_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='use_user_window',
            field=models.BooleanField(default=False),
        ),
    ]
