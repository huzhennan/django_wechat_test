# encoding=utf-8
from __future__ import absolute_import

import logging
import time
from datetime import datetime
from urllib import urlencode

import redis
import requests as http
from django.http import HttpResponse
from wechat_sdk import WechatConf, WechatBasic

TOKEN = u"ZaiHuiWanSui2015"
APP_ID = u"wxd1ac16e44122c49a"
APP_SECRET = u"d3ddce902a9d3c1f2071eb25f479df33"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

store = redis.StrictRedis(host='localhost', port=6379)


def client():
    c = WeClient(APP_ID, APP_SECRET, TOKEN, store=store)
    return c

class WebAuthMixin(object):
    """
    http://mp.weixin.qq.com/wiki/4/9ac2e7b1f1d22e9e57260f6553822520.html
    """
    def get_web_token(self, code):
        """
        通过code换取网页授权access_token(对应第二步)
        :param code:
        :return:
        """
        url = u"https://api.weixin.qq.com/sns/oauth2/access_token"
        params = (
            ('appid', self.app_id),
            ('secret', self.app_secret),
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

    @property
    def app_id(self):
        return NotImplementedError()

    @property
    def app_secret(self):
        return NotImplementedError()


class WeClient(WechatBasic, WebAuthMixin):
    ACCESS_TOKEN_KEY = u"access_token"
    JSAPI_TICKET_KEY = u"jsonapi_ticket"

    # access_token_getfunc 需要返回形如(token, expires_at)的数据
    # 可我们并不需要这个过期时间,由store存储管理
    # 给一个未来的时间
    EXPIRES_AT = (datetime(2999, 1, 1) - datetime(1970, 1, 1)).total_seconds()

    def __init__(self, app_id, app_secret, app_token, store):
        conf = WechatConf(
            appid=app_id,
            appsecret=app_secret,
            token=app_token,
            access_token_getfunc=self.get_access_token_func,
            jsapi_ticket_getfunc=self.get_jsapi_ticket_func,
        )
        WechatBasic.__init__(self, conf=conf)
        self.__app_id = app_id
        self.__app_secret = app_secret
        self.__app_token = app_token
        self.__store = store

    def get_access_token_func(self):
        token = self.store.get(WeClient.ACCESS_TOKEN_KEY)
        logger.debug(self.store.ttl(WeClient.ACCESS_TOKEN_KEY))
        if token:
            logger.debug("Get token from store")
            return token, WeClient.EXPIRES_AT
        else:
            logger.debug("Get token from request")
            json_ret = self.grant_token()
            token = json_ret[u'access_token']
            # 获取得到的有效期为`json_ret[u'expires_in']`,提前60s失效
            expires_in = int(json_ret[u'expires_in']) - 60
            store.setex(WeClient.ACCESS_TOKEN_KEY, expires_in, token)
            return token, WeClient.EXPIRES_AT

    def get_jsapi_ticket_func(self):
        ticket = self.store.get(WeClient.JSAPI_TICKET_KEY)
        if ticket:
            logger.debug("Get ticket from store")
            expires_at = time.time() + self.store.ttl(WeClient.JSAPI_TICKET_KEY)
            return ticket, expires_at
        else:
            logger.debug("Get ticket from request")
            json_ret = self.grant_jsapi_ticket()
            logger.debug(json_ret)
            ticket = json_ret[u'ticket']
            expires_in = int(json_ret[u'expires_in']) - 60
            store.setex(WeClient.JSAPI_TICKET_KEY, expires_in, ticket)
            expires_at = time.time() + expires_in
            return ticket, expires_at

    @property
    def store(self):
        return self.__store

    @property
    def app_id(self):
        return self.__app_id

    @property
    def app_secret(self):
        return self.__app_secret

    @property
    def app_token(self):
        return self.__app_token


class WeResponse(object):
    @staticmethod
    def check_signature(request):
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')

        import pdb
        pdb.set_trace()
        # TODO: 测试这里检查不通过, do something.
        if client().check_signature(signature, timestamp, nonce):
            print 'success'
        else:
            print 'something is wrong'
        return HttpResponse(echostr)

    @staticmethod
    def test_token():
        client().get_access_token()


if __name__ == '__main__':
    # print client().get_access_token()
    print "Result: %r" % client().get_jsapi_ticket()
    # print client().get_menu()
