# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-10 00:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20160509_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='difftrack',
            name='diff_composition_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='api.DiffCompositionVersion', verbose_name='Версия композиции'),
        ),
    ]