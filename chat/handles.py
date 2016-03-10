# encoding=utf-8
from __future__ import absolute_import

from .core import WeClient

TOKEN = u"ZaiHuiWanSui2015"
APP_ID = u"wxd1ac16e44122c49a"
APP_SECRET = u"d3ddce902a9d3c1f2071eb25f479df33"


def generate_test_menu(redirect_url='http://www.baidu.com'):
    client = WeClient(APP_ID, APP_SECRET, APP_SECRET)

    menu = {
        'button': [
            {
                'type': 'view',
                'name': 'BASE',
                'url': redirect_url
            },
            {
                'type': 'view',
                'name': 'SNSAPI_BASE',
                'url': client.generate_auth_url(redirect_url)
            },
            {
                'type': 'view',
                'name': 'SNSAPI_USERINFO',
                'url': client.generate_auth_url(redirect_url, scope='snsapi_userinfo')
            },
        ]
    }

    client = WeClient(APP_ID, APP_SECRET, APP_SECRET)
    client.create_menu(menu)


def get_open_id(code):
    client = WeClient(APP_ID, APP_SECRET, APP_SECRET)
    return client.get_open_id(code)
