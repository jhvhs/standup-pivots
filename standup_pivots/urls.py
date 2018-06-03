from django.conf.urls import include, url
from django.contrib import admin

from standup.views import index, slack_notification

urlpatterns = [
    url(r'^$', index),
    url(r'^slack_notification/$', slack_notification),
    url('^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
]
