# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import date
from django.core.validators import EmailValidator
from django.db import models
# noinspection PyUnresolvedReferences
from django.utils.encoding import python_2_unicode_compatible

from .validators import validate_monday


class Pivot(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, validators=(EmailValidator(),))
    slack_handle = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name

    @property
    def first_name(self):
        return self.full_name.split(' ')[0]


class Schedule(models.Model):
    standup_week_start = models.DateField(unique=True, validators=(validate_monday,))
    first_pivot = models.ForeignKey('Pivot', on_delete=models.SET_NULL, related_name="as_first_pivot", null=True)
    second_pivot = models.ForeignKey('Pivot', on_delete=models.SET_NULL, related_name="as_second_pivot", null=True)

    def __str__(self):
        return "Week of %s" % self.standup_week_start

    class Meta:
        ordering = ('standup_week_start',)

    @classmethod
    def current_schedule(cls, weekday_index=date.today().weekday()):
        if weekday_index < 5:
            qs = cls.objects.filter(standup_week_start__lte=date.today()).order_by('-standup_week_start')
        else:
            qs = cls.objects.filter(standup_week_start__gt=date.today())
        return qs.first()

    @classmethod
    def next_schedule(cls):
        return cls.current_schedule(6)
