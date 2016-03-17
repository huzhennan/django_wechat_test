from __future__ import absolute_import
import unittest

from wechat_lib.utils import generate_auth_url


class TestUtils(unittest.TestCase):
    def test_generate_auth_url(self):
        url = generate_auth_url('app_id', 'redirect_uri')
        self.assertEqual(url,
                         'https://open.weixin.qq.com/connect/oauth2/authorize?appid=app_id&redirect_uri=redirect_uri&response_type=code&scope=snsapi_base&state=test&component_appid=component_appid')

    def test_generate_auth_url_with_component_appid(self):
        url = generate_auth_url('APPID', 'REDIRECT_URI', scope='SCOPE', state='STATE',
                                component_appid='component_appid')
        self.assertEqual(url,
                         'https://open.weixin.qq.com/connect/oauth2/authorize?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE&component_appid=component_appid')
