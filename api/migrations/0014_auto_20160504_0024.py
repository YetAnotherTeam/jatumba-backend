# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-04 00:24
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20160503_1840'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiffCompositionVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('composition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diff_versions', to='api.Composition', verbose_name='Композиция')),
            ],
            options={
                'verbose_name': 'Дифф-версия композиции',
                'verbose_name_plural': 'Дифф-версии композиций',
            },
        ),
        migrations.CreateModel(
            name='DiffTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity', django.contrib.postgres.fields.jsonb.JSONField(null=True, verbose_name='Сущность')),
                ('order', models.PositiveSmallIntegerField(verbose_name='Порядок')),
                ('diff_composition_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diff_tracks', to='api.DiffCompositionVersion', verbose_name='Версия композиции')),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diff_tracks', to='api.Instrument', verbose_name='Инструмент')),
            ],
            options={
                'ordering': ('diff_composition_version', 'order'),
                'verbose_name': 'Дифф-дорожка',
                'verbose_name_plural': 'Дифф-дорожки',
            },
        ),
        migrations.AlterField(
            model_name='track',
            name='composition_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='api.CompositionVersion', verbose_name='Версия композиции'),
        ),
        migrations.AlterUniqueTogether(
            name='difftrack',
            unique_together=set([('diff_composition_version', 'order')]),
        ),
        migrations.AlterIndexTogether(
            name='diffcompositionversion',
            index_together=set([('composition', 'id')]),
        ),
    ]
