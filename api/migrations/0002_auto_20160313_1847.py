# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-13 18:47
from __future__ import unicode_literals

import api.models
import audiofield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Музыкальный жанр',
                'verbose_name_plural': 'Музыкальные жанры',
            },
        ),
        migrations.CreateModel(
            name='Sound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('file', audiofield.fields.AudioField(help_text='Allowed type - .mp3, .wav, .ogg', upload_to=api.models.instrument_sounds_path, verbose_name='Audio-файл')),
            ],
            options={
                'verbose_name': 'Звук',
                'verbose_name_plural': 'Звуки',
            },
        ),
        migrations.AlterField(
            model_name='instrument',
            name='name',
            field=models.CharField(max_length=25, unique=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='sound',
            name='instrument',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sounds', to='api.Instrument', verbose_name='Инструмент'),
        ),
        migrations.AddField(
            model_name='composition',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='compositions', to='api.Genre', verbose_name='Жанры'),
        ),
        migrations.AlterUniqueTogether(
            name='sound',
            unique_together=set([('instrument', 'name')]),
        ),
    ]
