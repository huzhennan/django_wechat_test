# encoding=utf-8
from __future__ import absolute_import

from django.conf.urls import url

from wechat_lib.we3rd_response import We3rdResponse
from wechat_lib.we_response import WeResponse
from . import views


app_name = 'chat'
urlpatterns = [
    url(r'^$', views.home, name='index'),
    url(r'^generate-menu$', views.generate_menu, name='generate_menu'),
    url(r'^open-id$', views.open_id, name='open_id'),
    # url(r'^(?P<app_id>\w+)/callback$', We3rdResponse.receive_verify_ticket, name='receive_verify_ticket'),


    url(r'^test_web_3rd/$', views.test_web_3rd, name='test_web_3rd'),
    url(r'^verify_ticket$', views.verify_ticket, name='verify_ticket'),
    url(r'^component_token$', views.component_token, name='component_token'),
    url(r'^pre_auth_code$', views.pre_auth_code, name='pre_auth_code'),
    url(r'^component_login_page$', views.component_login_page, name='component_login_page'),
    url(r'^auth_token$', views.auth_token, name='auth_token'),
    url(r'^web_3rd_operation', views.web_3rd_operation, name='web_3rd_operation'),

    url(r'^check-signature$', WeResponse.check_signature, name='check_signature'),
    url(r'^event_handler/$', We3rdResponse.event_handle, name='receive_verify_ticket'),
]
