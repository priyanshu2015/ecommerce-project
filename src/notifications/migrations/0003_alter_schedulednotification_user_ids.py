# Generated by Django 4.2.7 on 2023-12-10 08:35

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_alter_schedulednotification_scheduled_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulednotification',
            name='user_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, default=list, null=True, size=None),
        ),
    ]
