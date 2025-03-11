# Generated by Django 4.2.18 on 2025-03-11 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UbibotSensorTemp',
            fields=[
                ('timestamp', models.DateTimeField(primary_key=True, serialize=False, unique=True)),
                ('temp', models.FloatField(default=-1.0)),
            ],
        ),
    ]
