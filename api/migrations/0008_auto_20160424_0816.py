# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-24 08:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_add_order_to_tracks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='order',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Порядок'),
            preserve_default=False,
        ),
    ]