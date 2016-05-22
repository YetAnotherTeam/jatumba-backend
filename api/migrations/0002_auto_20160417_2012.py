# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-17 20:12
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollaborateTrackDiff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Сущность')),
            ],
            options={
                'verbose_name': 'Коллаборативное изменение дорожки',
                'verbose_name_plural': 'Коллаборативные изменения дорожек',
            },
        ),
        migrations.CreateModel(
            name='CollaborateTrackSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Дорожка')),
            ],
            options={
                'verbose_name': 'Коллаборативный снимок дорожки',
                'verbose_name_plural': 'Коллаборативные снимки дорожек',
            },
        ),
        migrations.CreateModel(
            name='CompositionBranch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('composition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='api.Composition', verbose_name='Композиция')),
            ],
            options={
                'verbose_name': 'Ветка',
                'verbose_name_plural': 'Ветки',
            },
        ),
        migrations.CreateModel(
            name='TrackDiff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Сущность')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diffs', to='api.CompositionBranch', verbose_name='Ветка')),
            ],
            options={
                'verbose_name': 'Изменение дорожки',
                'verbose_name_plural': 'Изменения дорожек',
            },
        ),
        migrations.CreateModel(
            name='TrackSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Дорожка')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='api.CompositionBranch', verbose_name='Ветка')),
            ],
            options={
                'verbose_name': 'Снимок дорожки',
                'verbose_name_plural': 'Снимки дорожки',
            },
        ),
        migrations.RemoveField(
            model_name='trackhistory',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='trackhistory',
            name='track_key',
        ),
        migrations.RemoveField(
            model_name='track',
            name='track',
        ),
        migrations.DeleteModel(
            name='TrackHistory',
        ),
        migrations.AddField(
            model_name='tracksnapshot',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='api.Track', verbose_name='Дорожка'),
        ),
        migrations.AddField(
            model_name='trackdiff',
            name='snapshot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diffs', to='api.TrackSnapshot', verbose_name='Снимок'),
        ),
        migrations.AddField(
            model_name='trackdiff',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diffs', to='api.Track', verbose_name='Дорожка'),
        ),
        migrations.AddField(
            model_name='collaboratetracksnapshot',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborate_snapshots', to='api.CompositionBranch', verbose_name='Ветка'),
        ),
        migrations.AddField(
            model_name='collaboratetracksnapshot',
            name='diff',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.CollaborateTrackDiff'),
        ),
        migrations.AddField(
            model_name='collaboratetracksnapshot',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborate_snapshots', to='api.Track', verbose_name='Коллаборативная дорожка'),
        ),
        migrations.AddField(
            model_name='collaboratetrackdiff',
            name='snapshot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaborate_diffs', to='api.TrackSnapshot', verbose_name='Снимок'),
        ),
    ]
