# encoding=utf-8
from __future__ import absolute_import

from .core import client


def generate_test_menu(redirect_url='http://www.baidu.com'):
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
                'url': client().generate_auth_url(redirect_url)
            },
            {
                'type': 'view',
                'name': 'SNSAPI_USERINFO',
                'url': client().generate_auth_url(redirect_url, scope='snsapi_userinfo')
            },
        ]
    }
    client().create_menu(menu)


def get_open_id(code):
    return client().get_open_id(code)
