from django.http import HttpResponse
from django.template.response import SimpleTemplateResponse

from .models import Schedule

SLACK_MESSAGE = "The standup hosts for the next week are <@{}> and <@{}>"


def index(request):
    current_schedule = Schedule.current_schedule()
    return SimpleTemplateResponse('index.html', {
        'schedule': current_schedule,
        'following_schedule': current_schedule.following_schedule,
    })


def slack_notification(request):
    schedule = Schedule.next_schedule()
    return HttpResponse(SLACK_MESSAGE.format(schedule.first_pivot.slack_handle, schedule.second_pivot.slack_handle))
