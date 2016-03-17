# encoding=utf-8
from __future__ import absolute_import

from chat.utils import generate_auth_url


def generate_test_menu(client, app_id, redirect_url='http://www.zaihuiba.com', component_appid=None):
    client.create_menu({
        'button': [
            {
                'type': 'view',
                'name': 'empty',
                'url': redirect_url
            },
            {
                'type': 'view',
                'name': 'BASE',
                'url': generate_auth_url(app_id, redirect_url, component_appid=component_appid)
            },
            {
                'type': 'view',
                'name': 'USERINFO',
                'url': generate_auth_url(app_id, redirect_url, scope='snsapi_userinfo', component_appid=component_appid)
            },
        ]})


def get_open_id(client, code):
    return client.get_open_id(code)
