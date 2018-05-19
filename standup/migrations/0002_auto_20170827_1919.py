# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-27 19:19
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import standup.validators


class Migration(migrations.Migration):

    dependencies = [
        ('standup', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pivot',
            name='email',
            field=models.CharField(max_length=255, validators=[django.core.validators.EmailValidator()]),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='standup_week_start',
            field=models.DateField(unique=True, validators=[standup.validators.validate_monday]),
        ),
    ]