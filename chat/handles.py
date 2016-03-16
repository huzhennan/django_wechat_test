# encoding=utf-8
from __future__ import absolute_import

from chat.utils import generate_auth_url


def generate_test_menu(client, redirect_url='http://www.baidu.com'):
    menu = {
        'button': [
            {
                'type': 'view',
                'name': 'BASE(test)',
                'url': redirect_url
            },
            {
                'type': 'view',
                'name': 'SNSAPI_BASE',
                'url': generate_auth_url(client.app_id, redirect_url)
            },
            {
                'type': 'view',
                'name': 'SNSAPI_USERINFO',
                'url': generate_auth_url(client.app_id, redirect_url, scope='snsapi_userinfo')
            },
        ]
    }
    client.create_menu(menu)


def get_open_id(client, code):
    return client.get_open_id(code)
