# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-06 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_auto_20171031_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='has_reply',
            field=models.BooleanField(default=False, verbose_name='has_reply'),
        ),
    ]
