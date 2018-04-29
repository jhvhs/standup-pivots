from datetime import date
from django.core.validators import EmailValidator
from django.db import models

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


class Standup(models.Model):
    week_start = models.DateField(unique=True, validators=(validate_monday,))
    first_pivot = models.ForeignKey('Pivot', on_delete=models.SET_NULL, related_name="as_first_pivot", null=True)
    second_pivot = models.ForeignKey('Pivot', on_delete=models.SET_NULL, related_name="as_second_pivot", null=True)

    def __str__(self):
        return "Week of %s" % self.week_start

    class Meta:
        ordering = ('week_start',)

    @classmethod
    def current_schedule(cls, weekday_index=date.today().weekday()):
        if weekday_index < 5:
            qs = cls.objects.filter(week_start__lte=date.today()).order_by('-week_start')
        else:
            qs = cls.objects.filter(week_start__gt=date.today())
        return qs.first()

    @classmethod
    def next_schedule(cls):
        return cls.current_schedule(6)

    @property
    def following_schedule(self):
        return self.__class__.objects.filter(week_start__gt=self.week_start).first()
