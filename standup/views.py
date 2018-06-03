from django.http import HttpResponse
from django.template.response import SimpleTemplateResponse

from .models import Standup

SLACK_MESSAGE = "The standup hosts for the next week are <@{}> and <@{}>"


def index(request):
    current_standup = Standup.current_standup()
    return SimpleTemplateResponse('index.html', {
        'standup': current_standup,
        'following_standup': current_standup.following_standup,
    })


def slack_notification(request):
    standup = Standup.next_standup()
    return HttpResponse(SLACK_MESSAGE.format(standup.first_pivot.slack_handle, standup.second_pivot.slack_handle))
