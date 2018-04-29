# coding=utf-8
from django.core.exceptions import ValidationError
from django.test import TestCase
from datetime import date, timedelta

from .models import Pivot, Standup
from .validators import validate_monday


# noinspection PyMethodMayBeStatic
class DublinStandupTestCase(TestCase):
    def setUp(self):
        self.today = date.today()
        self.next_week = self.today + timedelta(7)

    def insert_schedule_fixtures(self):
        pivot = Pivot.objects.create(full_name="Won Ton Goodsoup", email="wonton@goodsoups.info", slack_handle="wtd")
        Standup.objects.create(week_start=self.today, first_pivot=pivot, second_pivot=pivot)
        Standup.objects.create(week_start=self.next_week, first_pivot=pivot, second_pivot=pivot)

    def test_valid_pivot(self):
        pivot = Pivot(full_name="foo", email="bar@baz.com", slack_handle="jimmy")
        pivot.full_clean()

    def test_pivot_with_invalid_email(self):
        pivot = Pivot(full_name="foo", email="bar", slack_handle="jimmy")
        self.assertRaises(ValidationError, pivot.full_clean)

    def test_schedule_with_valid_date(self):
        schedule = Standup(week_start=date(2017, 9, 4))
        schedule.clean_fields(exclude=('first_pivot', 'second_pivot'))

    def test_schedule_with_invalid_date(self):
        schedule = Standup(week_start=date(2017, 9, 5))
        self.assertRaises(ValidationError, lambda: schedule.clean_fields(exclude=('first_pivot', 'second_pivot')))

    def test_monday_validator_with_mondays(self):
        mondays = (date(2017, 9, 4), date(2017, 10, 2), date(2017, 10, 9))
        for d in mondays:
            validate_monday(d)

    def test_monday_validator_with_other_days(self):
        other_days = (date(2017, 9, 5), date(2017, 9, 6), date(2017, 9, 7), date(2017, 9, 8),
                      date(2017, 9, 9), date(2017, 9, 10), date(2017, 9, 12), date(2017, 9, 13),)
        for d in other_days:
            self.assertRaises(ValidationError, lambda: validate_monday(d))

    def test_current_schedule(self):
        self.insert_schedule_fixtures()
        for i in range(5):
            self.assertEqual(Standup.current_schedule(i).week_start, self.today)
        for i in range(5, 7):
            self.assertEqual(Standup.current_schedule(i).week_start, self.next_week)

    def test_next_schedule(self):
        self.insert_schedule_fixtures()
        self.assertEqual(Standup.next_schedule().week_start, self.next_week)

    def test_pivot_name(self):
        pivot = Pivot(full_name=u"Jelomjúsø van der Vękūblmsti")
        self.assertEqual(pivot.first_name, u"Jelomjúsø")

    def test_following_schedule(self):
        self.insert_schedule_fixtures()
        schedule = Standup.current_schedule(1)
        self.assertEqual(schedule.week_start, self.today)
        self.assertEqual(schedule.following_schedule.week_start, self.next_week)
