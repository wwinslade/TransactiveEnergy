# Generated by Django 4.2.18 on 2025-02-11 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='New Device', max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('device_type', models.CharField(default='Unknown', max_length=50)),
                ('status', models.BooleanField(default=False)),
                ('ipv4', models.GenericIPAddressField(blank=True, null=True)),
                ('sync_or_async', models.CharField(default='sync', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
