# encoding=utf-8
from __future__ import absolute_import

import logging
import time

from wechat_sdk import WechatConf, WechatBasic

from .conf import EXPIRES_AT, store
from .store_key import ACCESS_TOKEN_KEY, JSAPI_TICKET_KEY
from . import http

logger = logging.getLogger(__name__)


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
        return r

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
    def __init__(self, app_id, app_secret, app_token, store, encrypt_mode='normal'):
        conf = WechatConf(
            appid=app_id,
            appsecret=app_secret,
            token=app_token,
            encrypt_mode=encrypt_mode,
            access_token_getfunc=self.get_access_token_func,
            jsapi_ticket_getfunc=self.get_jsapi_ticket_func,
        )
        WechatBasic.__init__(self, conf=conf)
        self.__app_id = app_id
        self.__app_secret = app_secret
        self.__app_token = app_token
        self.__store = store

    def get_access_token_func(self):
        token = self.store.get(ACCESS_TOKEN_KEY)
        logger.debug(self.store.ttl(ACCESS_TOKEN_KEY))
        if token:
            logger.debug("Get token from store")
            return token, EXPIRES_AT
        else:
            logger.debug("Get token from request")
            json_ret = self.grant_token()
            token = json_ret[u'access_token']
            # 获取得到的有效期为`json_ret[u'expires_in']`,提前60s失效
            expires_in = int(json_ret[u'expires_in']) - 60
            store.setex(ACCESS_TOKEN_KEY, expires_in, token)
            return token, EXPIRES_AT

    def get_jsapi_ticket_func(self):
        ticket = self.store.get(JSAPI_TICKET_KEY)
        if ticket:
            logger.debug("Get ticket from store")
            expires_at = time.time() + self.store.ttl(JSAPI_TICKET_KEY)
            return ticket, expires_at
        else:
            logger.debug("Get ticket from request")
            json_ret = self.grant_jsapi_ticket()
            logger.debug(json_ret)
            ticket = json_ret[u'ticket']
            expires_in = int(json_ret[u'expires_in']) - 60
            store.setex(JSAPI_TICKET_KEY, expires_in, ticket)
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