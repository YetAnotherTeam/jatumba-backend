# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 19:56
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_auto_20160613_0100'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='create_datetime',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 8, 2, 19, 56, 48, 462753, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
