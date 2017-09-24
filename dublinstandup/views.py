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
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.response import SimpleTemplateResponse
try:
    from google.appengine.api import mail
except ImportError:
    import gmail_dummy as mail

from .models import Schedule

SENDER = "reminder-bot@cf-pcf-kubo.appspotmail.com"
SUBJECT = "You have been chosen to lead the standup next week"
MESSAGE = """Hi {},

You and {} have been chosen to run the standup next week.
Please make sure to come to the office a bit earlier.

Yours truly,

The Dublin Standup Bot 
                   """


def index(request):
    current_schedule = Schedule.current_schedule()
    return SimpleTemplateResponse('index.html', {
        'schedule': current_schedule,
        'following_schedule': current_schedule.following_schedule,
    })


def notify(request):
    if request.META.get('HTTP_X_APPENGINE_CRON') != 'true':
        raise PermissionDenied()

    schedule = Schedule.next_schedule()
    first_pivot = schedule.first_pivot
    second_pivot = schedule.second_pivot

    mail.send_mail(
        sender=SENDER,
        to="{} <{}>".format(first_pivot.full_name, first_pivot.email),
        subject=SUBJECT,
        body=MESSAGE.format(first_pivot.first_name, second_pivot.first_name)
    )

    mail.send_mail(
        sender=SENDER,
        to="{} <{}>".format(second_pivot.full_name, second_pivot.email),
        subject=SUBJECT,
        body=MESSAGE.format(second_pivot.first_name, first_pivot.first_name)
    )

    return HttpResponse("{} and {} have been notified".format(first_pivot, second_pivot))
