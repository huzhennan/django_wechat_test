# encoding=utf-8
import urllib

import requests as http
from django.http import HttpResponse
from wechat_sdk import WechatConf, WechatBasic

TOKEN = u"ZaiHuiWanSui2015"
APP_ID = u"wxd1ac16e44122c49a"
APP_SECRET = u"d3ddce902a9d3c1f2071eb25f479df33"


def client():
    c = WeClient(APP_ID, APP_SECRET, APP_SECRET)
    return c


def generate_url(base_url, params):
    return base_url + "?" + urllib.urlencode(params)


class WebAuthMixin(object):
    """
    http://mp.weixin.qq.com/wiki/4/9ac2e7b1f1d22e9e57260f6553822520.html
    """

    def generate_auth_url(self, redirect_uri, scope='snsapi_base', state='test'):
        """
        生成网页制授权页面(对应第一步:用户同意授权，获取code)
        :param redirect_uri: 授权后重定向的回调链接地址，请使用urlencode对链接进行处理
        :param scope: 应用授权作用域，snsapi_base （不弹出授权页面，直接跳转，只能获取用户openid）,
        snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。
        :param state: 重定向后会带上state参数，开发者可以填写a-zA-Z0-9的参数值，最多128字节
        :return:
        """
        params = [
            ('appid', self.app_id()),
            ('redirect_uri', redirect_uri),
            ('response_type', 'code'),
            ('scope', scope),
            ('state', state)
        ]
        return generate_url('https://open.weixin.qq.com/connect/oauth2/authorize', params)

    def get_web_token(self, code):
        """
        通过code换取网页授权access_token(对应第二步)
        :param code:
        :return:
        """
        url = u"https://api.weixin.qq.com/sns/oauth2/access_token"
        params = (
            ('appid', self.app_id()),
            ('secret', self.app_secret()),
            ('code', code),
            ('grant_type', 'authorization_code')
        )

        r = http.get(url, params=params)
        return r.json()

    def get_open_id(self, code):
        """
        获取open_id, 从access_token信息中
        :param code:
        :return:
        """
        return self.get_web_token(code)[u'openid']

    def app_id(self):
        return NotImplementedError()

    def app_secret(self):
        return NotImplementedError()


class WeBaseMixin(object):
    def app_id(self):
        return NotImplementedError()

    def app_secret(self):
        return NotImplementedError()

    def app_token(self):
        return NotImplementedError()


class WeClient(WechatBasic, WebAuthMixin, WeBaseMixin):
    def __init__(self, app_id, app_secret, app_token):
        WechatBasic.__init__(self, token=app_token, appid=app_id, appsecret=app_secret)
        self.__app_id = app_id
        self.__app_secret = app_secret
        self.__app_token = app_token

    def app_id(self):
        return self.__app_id

    def app_secret(self):
        return self.__app_secret

    def app_token(self):
        return self.__app_token


class WeRespond(object):
    @staticmethod
    def check_signature(request):
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')

        if client().check_signature(signature, timestamp, nonce):
            print 'success'
        else:
            print 'something is wrong'

        return HttpResponse(echostr)


class Web3rdClient(object):
    def pre_auth_code(self, component_appid):
        url = u"https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode"
