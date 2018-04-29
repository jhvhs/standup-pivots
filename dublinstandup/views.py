from django.http import HttpResponse
from django.template.response import SimpleTemplateResponse

from .models import Standup

SLACK_MESSAGE = "The standup hosts for the next week are <@{}> and <@{}>"


def index(request):
    current_schedule = Standup.current_schedule()
    return SimpleTemplateResponse('index.html', {
        'schedule': current_schedule,
        'following_schedule': current_schedule.following_schedule,
    })


def slack_notification(request):
    schedule = Standup.next_schedule()
    return HttpResponse(SLACK_MESSAGE.format(schedule.first_pivot.slack_handle, schedule.second_pivot.slack_handle))
