# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 18:27
from __future__ import unicode_literals

import api.models.dictionary
import audiofield.fields
from django.db import migrations, models
import django.db.models.deletion
import utils.django.storage


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20160419_0734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compositionversion',
            name='composition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='api.Composition', verbose_name='Композиция'),
        ),
        migrations.AlterField(
            model_name='sound',
            name='file',
            field=audiofield.fields.AudioField(help_text='Allowed type - .mp3, .wav, .ogg', storage=utils.django.storage.OverwriteStorage(), upload_to=api.models.dictionary.sounds_path, verbose_name='Audio-файл'),
        ),
    ]