# encoding=utf-8
from __future__ import absolute_import

from .core import WeClient

TOKEN = u"ZaiHuiWanSui2015"
APP_ID = u"wxd1ac16e44122c49a"
APP_SECRET = u"d3ddce902a9d3c1f2071eb25f479df33"


def generate_menu_handle():
    menu = {
        'button': [
            {
                'type': 'view',
                'name': 'BASE',
                'url': 'http://www.zaihuiba.com/kata/menu'
            },
            {
                'type': 'view',
                'name': 'SNSAPI_BASE',
                'url': 'http://www.zaihuiba.com/kata/menu'
            },
            {
                'type': 'view',
                'name': 'SNSAPI_USERINFO',
                'url': 'http://www.zaihuiba.com/kata/menu'
            },
        ]
    }

    client = WeClient(APP_ID, APP_SECRET, APP_SECRET)
    client.create_menu(menu)
