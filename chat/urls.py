# encoding=utf-8
from __future__ import absolute_import

from django.conf.urls import url

from . import views

app_name = 'chat'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^generate-menu$', views.generate_menu, name='generate_menu')
]

