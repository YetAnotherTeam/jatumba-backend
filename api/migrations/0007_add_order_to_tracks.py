# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-24 08:06
from __future__ import unicode_literals

from django.db import migrations


def forward(apps, schema_editor):
    CompositionVersion = apps.get_model('api', 'CompositionVersion')
    for composition_version in CompositionVersion.objects.prefetch_related('tracks'):
        order = 1
        for track in composition_version.tracks.all():
            track.order = order
            track.save()
            order += 1


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0006_auto_20160424_0813'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]