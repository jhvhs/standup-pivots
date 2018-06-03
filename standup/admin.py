from datetime import date
from django.contrib import admin
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from .models import Pivot, Standup


class StandupListFilter(admin.SimpleListFilter):
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
            return queryset.filter(week_start__gte=date.today())
        if self.value() == 'all':
            return queryset
        if self.value() == 'past':
            return queryset.filter(week_start__lt=date.today())


class PivotAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'slack_handle', 'has_left_the_office')
    ordering = ('full_name',)
    list_filter = ('has_left_the_office',)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('week_start', 'first_pivot', 'second_pivot')
    ordering = ('week_start',)
    list_filter = (StandupListFilter,)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['adminform'].form.fields['first_pivot'].queryset = Pivot.available()
        context['adminform'].form.fields['second_pivot'].queryset = Pivot.available()
        return super(ScheduleAdmin, self).render_change_form(request, context, add, change, form_url, obj)


admin.site.register(Pivot, PivotAdmin)
admin.site.register(Standup, ScheduleAdmin)
