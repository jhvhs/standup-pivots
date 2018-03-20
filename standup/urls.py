from django.conf.urls import include, url
from django.contrib import admin

from dublinstandup.views import index, slack_notification

urlpatterns = [
    url(r'^$', index),
    url(r'^slack_notification/$', slack_notification),
    url(r'^admin/', include(admin.site.urls)),
]
