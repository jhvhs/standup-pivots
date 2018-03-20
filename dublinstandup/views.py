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
from django.http import HttpResponse
from django.template.response import SimpleTemplateResponse

from .models import Schedule

SENDER = "reminder-bot@cf-pcf-kubo.appspotmail.com"
SUBJECT = "You have been chosen to lead the standup next week"
MESSAGE = """Hi {},

You and {} have been chosen to run the standup next week.
Please make sure to come to the office a bit earlier.

Yours truly,

The Dublin Standup Bot 
                   """

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
