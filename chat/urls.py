# encoding=utf-8
from __future__ import absolute_import

from django.conf.urls import url

from . import views
from .core import WeRespond

app_name = 'chat'
urlpatterns = [
url(r'^$', views.index, name='index'),
    url(r'^generate-menu$', views.generate_menu, name='generate_menu'),
    url(r'^open-id$', views.open_id, name='open_id'),
    url(r'^check-signature$', WeRespond.check_signature, name='check_signature')
]

