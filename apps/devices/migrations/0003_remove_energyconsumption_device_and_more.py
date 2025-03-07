# Generated by Django 4.2.18 on 2025-02-25 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_energyconsumption'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='energyconsumption',
            name='device',
        ),
        migrations.AddField(
            model_name='energyconsumption',
            name='label',
            field=models.CharField(default='Unspecified', max_length=100),
        ),
        migrations.AlterField(
            model_name='energyconsumption',
            name='energy_consumed',
            field=models.FloatField(default=0.0),
        ),
    ]
