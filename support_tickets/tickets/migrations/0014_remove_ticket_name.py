# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-25 20:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0013_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='name',
        ),
    ]
