from datetime import date
from django.contrib import admin
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from .models import Pivot, Schedule


class ScheduleListFilter(admin.SimpleListFilter):
    title = _("standup weeks")

    parameter_name = 'schedule_dates'

    def lookups(self, request, model_admin):
        return (
            (None, _('Active')),
            ('all', _('All')),
            ('past', _('Past')),
        )

    def choices(self, changelist):
        for value, title in self.lookups(None, None):
            if value is None:
                query_string = changelist.get_query_string({}, [self.parameter_name])
            else:
                query_string = changelist.get_query_string({self.parameter_name: value}, [])
            yield {
                'selected': ((self.value() is None) and (value is None)) or self.value() == force_text(value),
                'query_string': query_string,
                'display': title
            }

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(standup_week_start__gte=date.today())
        if self.value() == 'all':
            return queryset
        if self.value() == 'past':
            return queryset.filter(standup_week_start__lt=date.today())


class PivotAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'slack_handle')
    ordering = ('full_name',)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('standup_week_start', 'first_pivot', 'second_pivot')
    ordering = ('standup_week_start',)
    list_filter = (ScheduleListFilter,)


admin.site.register(Pivot, PivotAdmin)
admin.site.register(Schedule, ScheduleAdmin)
