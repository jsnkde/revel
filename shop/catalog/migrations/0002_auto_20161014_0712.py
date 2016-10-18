# -*- coding: utf-8 -*-
# Generated by Django 1.11.dev20161011233113 on 2016-10-14 07:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
