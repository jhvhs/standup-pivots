# coding=utf-8
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.test import TestCase
from datetime import date, timedelta

from .models import Pivot, Standup
from .validators import validate_monday


# noinspection PyMethodMayBeStatic
class StandupTestCase(TestCase):
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


# noinspection PyMethodMayBeStatic
class StandupDatasetTestCase(TestCase):
    fixtures = ("dataset.json",)
    last_standup_week_date = "2018-05-28"
    last_assigned_pivot_id = 10
    departed_pivot_id = 5

    def test_new_standup_assignment(self):
        Standup.plan(2)
        scheduled_standups = Standup.objects.filter(week_start__gt=self.last_standup_week_date)
        self.assertEqual(scheduled_standups.count(), 2, "Expected 2 new standups to be scheduled")

    def test_new_standup_assignees(self):
        Standup.plan(2)
        for s in Standup.objects.filter(week_start__gt=self.last_standup_week_date).all():
            self.assertGreater(s.first_pivot_id, self.last_assigned_pivot_id)
            self.assertGreater(s.second_pivot_id, self.last_assigned_pivot_id)

    def test_available_pivots(self):
        self.assertEqual(Pivot.available().count(), 13)

    def test_next_pivot_for_standup(self):
        next_pivot = Pivot.next_pivot_for_standup()
        self.assertGreater(next_pivot.id, self.last_assigned_pivot_id)

    def test_standup_rotation(self):
        Standup.plan(2)
        next_pivot = Pivot.next_pivot_for_standup()
        self.assertIsNotNone(next_pivot.id)

    def test_next_pivot_randomness(self):
        standup_pivot_ids = [Pivot.new_pivot_for_standup().id for _ in range(4)]
        self.assertGreater(len(set(standup_pivot_ids)), 1)

    def test_departed_pivots_are_not_assigned(self):
        Standup.plan(12)
        scheduled_standups = Standup.objects.filter(week_start__gt=self.last_standup_week_date).exclude(
            first_pivot_id=self.departed_pivot_id).exclude(second_pivot_id=self.departed_pivot_id)
        self.assertEqual(scheduled_standups.count(), 12)
