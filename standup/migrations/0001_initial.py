# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-27 12:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pivot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('slack_handle', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('standup_week_start', models.DateField(unique=True)),
                ('first_pivot', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='as_first_pivot', to='standup.Pivot')),
                ('second_pivot', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='as_second_pivot', to='standup.Pivot')),
            ],
        ),
    ]
