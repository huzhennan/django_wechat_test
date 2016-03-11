# encoding=utf-8
from __future__ import absolute_import

from django.conf.urls import url

from chat.core3rd import We3rdResponse
from . import views
from .core import WeResponse

app_name = 'chat'
urlpatterns = [
url(r'^$', views.index, name='index'),
    url(r'^generate-menu$', views.generate_menu, name='generate_menu'),
    url(r'^open-id$', views.open_id, name='open_id'),
    url(r'^check-signature$', WeResponse.check_signature, name='check_signature'),
    # url(r'^(?P<app_id>\w+)/callback$', We3rdResponse.receive_verify_ticket, name='receive_verify_ticket'),
    url(r'^event_handler$', We3rdResponse.receive_verify_ticket, name='receive_verify_ticket'),
]

