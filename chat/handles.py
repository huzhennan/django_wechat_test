# encoding=utf-8
from __future__ import absolute_import

from chat.utils import generate_auth_url


def generate_test_menu(client, app_id, redirect_url='http://www.baidu.com', component_appid=None):
    client.create_menu({
        'button': [
            {
                'type': 'click',
                'name': 'hzn',
                'key': 'V1001_TODAY_MUSIC'
            },
            {
                'type': 'click',
                'name': '歌手简介',
                'key': 'V1001_TODAY_SINGER'
            },
            {
                'name': '菜单',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '搜索',
                        'url': 'http://www.soso.com/'
                    },
                    {
                        'type': 'view',
                        'name': '视频',
                        'url': 'http://v.qq.com/'
                    },
                    {
                        'type': 'click',
                        'name': '赞一下我们',
                        'key': 'V1001_GOOD'
                    }
                ]
            }
        ]})


def get_open_id(client, code):
    return client.get_open_id(code)
