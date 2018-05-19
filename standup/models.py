from datetime import date, timedelta
from random import choice

from django.core.validators import EmailValidator
from django.db import models
from django.db.models import Max, Q

from .validators import validate_monday


class Pivot(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, validators=(EmailValidator(),))
    slack_handle = models.CharField(max_length=255)
    has_left_the_office = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    @property
    def first_name(self):
        return self.full_name.split(' ')[0]

    @classmethod
    def available(cls):
        return cls.objects.filter(has_left_the_office=False)

    @classmethod
    def next_pivot_for_standup(cls):
        new_pivot = cls.new_pivot_for_standup()
        if new_pivot:
            return new_pivot
        return Pivot()

    @classmethod
    def new_pivot_for_standup(cls):
        new_pivots = cls.available().filter(as_first_pivot__isnull=True, as_second_pivot__isnull=True)
        if new_pivots.count() == 0:
            skip_weeks = cls.available().count() / 5
            skipped_pivots = cls._ids_for_pivots_running_standups_over_last_weeks(skip_weeks)
            new_pivots = cls.available().exclude(pk__in=skipped_pivots)
        new_id = choice(new_pivots.values_list('id', flat=True))
        return cls.objects.get(pk=new_id)

    @classmethod
    def _ids_for_pivots_running_standups_over_last_weeks(cls, number_of_weeks):
        last_scheduled_standup = Standup.objects.aggregate(Max("week_start"))['week_start__max']
        skip_upto_date = last_scheduled_standup - timedelta(weeks=number_of_weeks - 1)
        recent_first_pivots = Pivot.objects.annotate(f=Max('as_first_pivot__week_start')).filter(f__gt=skip_upto_date)
        recent_second_pivots = Pivot.objects.annotate(s=Max('as_second_pivot__week_start')).filter(s__gt=skip_upto_date)
        return (recent_first_pivots | recent_second_pivots).distinct().values_list('id', flat=True)


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

    @classmethod
    def plan(cls, week_count):
        last_date = cls.objects.aggregate(Max("week_start"))['week_start__max']
        for i in range(week_count):
            offset = timedelta(weeks=1 + i)
            first_pivot = Pivot.new_pivot_for_standup()
            second_pivot = Pivot.new_pivot_for_standup()
            while second_pivot == first_pivot:
                second_pivot = Pivot.new_pivot_for_standup()
            cls(week_start=last_date + offset, first_pivot=first_pivot, second_pivot=second_pivot).save()
