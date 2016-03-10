# encoding=utf-8
import urllib

import requests as http
from wechat_sdk import WechatConf, WechatBasic


def generate_url(base_url, params):
    return base_url + "?" + urllib.urlencode(params)


class WeAuthMixin(object):
    def generate_auth_url(self, redirect_uri, scope='snsapi_base', state='test'):
        params = [
            ('appid', self.app_id()),
            ('redirect_uri', redirect_uri),
            ('response_type', 'code'),
            ('scope', scope),
            ('state', state)
        ]
        return generate_url('https://open.weixin.qq.com/connect/oauth2/authorize', params)

    def get_access_token(self, code):
        url = self.__base_url() + "access_token"
        params = {
            'appid': self.app_id(),
            'secret': self.app_secret(),
            'code': code,
            'grant_type': 'authorization_code'
        }

        r = http.get(url, params=params)
        return r.json()

    def get_open_id(self, code):
        return self.get_access_token(code)

    def __base_url(self):
        return u"https://open.weixin.qq.com/connect/oauth2/"

    def app_id(self):
        return NotImplementedError()

    def app_secret(self):
        return NotImplementedError()


class WeBaseMixin(object):
    def create_menu(self, menu_data):
        conf = WechatConf(
            token=self.app_token(),
            appid=self.app_id(),
            appsecret=self.app_secret(),
            encrypt_mode="normal"
        )
        wechat = WechatBasic(conf=conf)
        return wechat.create_menu(menu_data)

    def app_id(self):
        return NotImplementedError()

    def app_secret(self):
        return NotImplementedError()

    def app_token(self):
        return NotImplementedError()


class WeClient(WeAuthMixin, WeBaseMixin):
    def __init__(self, app_id, app_secret, app_token):
        self.__app_id = app_id
        self.__app_secret = app_secret
        self.__app_token = app_token

    def app_id(self):
        return self.__app_id

    def app_secret(self):
        return self.__app_secret

    def app_token(self):
        return self.__app_token
