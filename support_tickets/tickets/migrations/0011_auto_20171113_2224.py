# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-13 22:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0010_auto_20171113_1117'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='ticket_uuid',
            new_name='uuid',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='has_reply',
        ),
    ]
