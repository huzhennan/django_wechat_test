# encoding=utf-8
import json
import logging
from urllib import urlencode

import redis
import requests as http
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatConf, WechatBasic
from wechat_sdk.exceptions import ParseError, NeedParseError
from wechat_sdk.lib.parser import XMLStore
from wechat_sdk.messages import MESSAGE_TYPES, UnknownMessage

from chat.keeper import Keeper

logger = logging.getLogger(__name__)

APP_ID = u'wx67c082d3d5c5c355'
APP_SECRET = u'7678827bbe43445e4fb6631cd96e02dc'
TOKEN = u'ZaiHuiNiuBi20151102'
SYMMETRIC_KEY = u'yBUilBquwak6qAzuL1U04JrFSjwDjukjDoFjPRuLCU2'

store = redis.StrictRedis(host='localhost', port=6379)


def client3rd():
    c = We3rdClient(APP_ID, APP_SECRET, TOKEN, SYMMETRIC_KEY, store=store)
    return c


def generate_url(base_url, params):
    return base_url + "?" + urlencode(params)


class Web3rdAuthMixin(object):
    COMPONENT_VERIFY_TICKET_KEY = u"component_verify_ticket"
    COMPONENT_ACCESS_TOKEN_KEY = u"component_access_token"
    PRE_AUTH_CODE_KEY = u"pre_auth_code"
    AUTH_ACCESS_TOKE_KEY = u"auth_%s_authorizer_access_token"

    def get_pre_auth_code(self):
        keeper = Keeper(self.store,
                        gain_func=self._gain_pre_auth_code)
        ret = keeper.get(Web3rdAuthMixin.PRE_AUTH_CODE_KEY)
        return ret.get(u'pre_auth_code')

    def _gain_pre_auth_code(self):
        token = self.get_component_access_token()
        params = {
            u'component_access_token': token
        }
        url = generate_url(u"https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode", params)

        json_data = {
            u"component_appid": self.app_id
        }
        return http.post(url, json=json_data).json()

    def get_component_access_token(self):
        keeper = Keeper(self.store,
                        gain_func=self._gain_component_access_token,
                        shorten=60 * 10)
        ret = keeper.get(Web3rdAuthMixin.COMPONENT_ACCESS_TOKEN_KEY)
        return ret.get(u'component_access_token')

    def _gain_component_access_token(self):
        url = u"https://api.weixin.qq.com/cgi-bin/component/api_component_token"
        data = {
            u"component_appid": self.app_id,
            u"component_appsecret": self.app_secret,
            u"component_verify_ticket": self.verify_ticket
        }
        logging.info("data: %r", data)
        return http.post(url, json=data).json()

    def generate_component_login_page(self, redirect_uri):
        params = (
            (u'component_appid', self.app_id),
            (u'pre_auth_code', self.get_pre_auth_code()),
            (u'redirect_uri', redirect_uri)
        )
        return generate_url(u'https://mp.weixin.qq.com/cgi-bin/componentloginpage', params=params)

    def api_query_auth(self, auth_code):
        params = (
            (u"component_access_token", self.get_component_access_token()),
        )
        url = generate_url(u"https://api.weixin.qq.com/cgi-bin/component/api_query_auth", params=params)
        data = {
            u"component_appid": self.app_id,
            u"authorization_code": auth_code
        }
        return http.post(url, json=data).json()

    def api_authorizer_token(self, auth_appid):
        params = (
            (u"component_access_token", self.get_component_access_token()),
        )
        url = generate_url(u"https:// api.weixin.qq.com /cgi-bin/component/api_authorizer_token", params=params)
        data = {
            u"component_appid": self.app_id,
            u"authorizer_appid": auth_appid,
            u"authorizer_refresh_token": self._refresh_token(auth_appid)
        }
        ret = http.post(url, json=data).json()
        return ret['authorizer_access_token']

    def get_authorizer_token(self, auth_appid):
        keeper = Keeper(self.store,
                        gain_func=self.api_query_auth,
                        gain_args={'auth_appid': auth_appid})
        key = Web3rdAuthMixin.AUTH_ACCESS_TOKE_KEY % auth_appid
        return keeper.get(key)

    def _refresh_token(self, auth_appid):
        keeper = Keeper(self.store)
        key = Web3rdAuthMixin.AUTH_ACCESS_TOKE_KEY % auth_appid
        return keeper.get(key)

    @property
    def verify_ticket(self):
        keeper = Keeper(self.store)
        return keeper.get(Web3rdAuthMixin.COMPONENT_VERIFY_TICKET_KEY)

    @verify_ticket.setter
    def verify_ticket(self, ticket):
        keeper = Keeper(self.store)
        keeper.setex(Web3rdAuthMixin.COMPONENT_VERIFY_TICKET_KEY, 60 * 10, ticket)

    @property
    def store(self):
        raise NotImplementedError()

    @property
    def app_id(self):
        raise NotImplementedError()

    @property
    def app_secret(self):
        raise NotImplementedError()


class RewriteMixin(object):
    """
    用来覆盖`WechatBasic`的几个函数
    """

    def parse_data(self, data, msg_signature=None, timestamp=None, nonce=None):
        """
        解析微信服务器发送过来的数据并保存类中
        :param data: HTTP Request 的 Body 数据
        :param msg_signature: EncodingAESKey 的 msg_signature
        :param timestamp: EncodingAESKey 用时间戳
        :param nonce: EncodingAESKey 用随机数
        :raises ParseError: 解析微信服务器数据错误, 数据不合法
        """
        result = {}
        if type(data) not in [str, unicode]:
            raise ParseError()

        data = data.encode('utf-8')

        if self.conf.encrypt_mode == 'safe':
            if not (msg_signature and timestamp and nonce):
                raise ParseError('must provide msg_signature/timestamp/nonce in safe encrypt mode')

            data = self.conf.crypto.decrypt_message(
                msg=data,
                msg_signature=msg_signature,
                timestamp=timestamp,
                nonce=nonce,
            )
        try:
            xml = XMLStore(xmlstring=data)
        except Exception:
            raise ParseError()

        result = xml.xml2dict
        result['raw'] = data

        try:
            result['type'] = result.pop('MsgType').lower()
            message_type = MESSAGE_TYPES.get(result['type'], UnknownMessage)
            self.__message = message_type(result)
        except KeyError:
            self.__message = UnknownMessage(result)
        self.__is_parse = True

    def get_message(self):
        """
        获取解析好的 WechatMessage 对象
        :return: 解析好的 WechatMessage 对象
        """
        self._check_parse()

        return self.__message

    def _check_parse(self):
        """
        检查是否成功解析微信服务器传来的数据
        :raises NeedParseError: 需要解析微信服务器传来的数据
        """
        if not self.__is_parse:
            raise NeedParseError()


class We3rdClient(RewriteMixin, WechatBasic, Web3rdAuthMixin):
    def __init__(self, app_id, app_secret, app_token, encoding_aes_key, store, encrypt_mode='safe'):
        conf = WechatConf(
            appid=app_id,
            appsecret=app_secret,
            token=app_token,
            encrypt_mode=encrypt_mode,
            encoding_aes_key=encoding_aes_key
        )
        WechatBasic.__init__(self, conf=conf)
        self.__app_id = app_id
        self.__app_secret = app_secret
        self.__store = store

    @property
    def store(self):
        return self.__store

    @property
    def app_id(self):
        return self.__app_id

    @property
    def app_secret(self):
        return self.__app_secret


class We3rdResponse(object):
    @staticmethod
    @csrf_exempt
    def event_handle(request):
        msg_signature = request.GET.get(u'msg_signature')
        timestamp = request.GET.get(u'timestamp')
        nonce = request.GET.get(u'nonce')

        auth_code = request.GET.get(u'auth_code')
        expires_in = request.GET.get(u'expires_in')

        if msg_signature is not None and timestamp is not None and nonce is not None:
            return We3rdResponse.ticket_handler(request, msg_signature, timestamp, nonce)
        elif auth_code is not None and expires_in is not None:
            return We3rdResponse.auth_handle(request, auth_code, expires_in)
        else:
            raise NotImplementedError("something is wrong.")

    @staticmethod
    def ticket_handler(request, msg_signature, timestamp, nonce):
        client = client3rd()
        client.parse_data(data=request.body, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
        msg = client.get_message()

        verify_ticket = msg.ComponentVerifyTicket
        expires_in = 10 * 60

        keeper = Keeper(client.store)
        keeper.setex(We3rdClient.COMPONENT_VERIFY_TICKET_KEY, expires_in, verify_ticket)

        logger.info("I gains a  ticket: %r, expires_in: %r", verify_ticket, expires_in)
        return HttpResponse(u"success")

    @staticmethod
    def auth_handle(request, auth_code, expires_in):
        client = client3rd()
        ret = client.api_query_auth(auth_code)
        auth_info = ret[u'authorization_info']

        keeper = Keeper(client.store)

        key = u"auth_%s_authorizer_access_token" % auth_info[u'authorizer_appid']
        value = auth_info[u'authorizer_access_token']

        # 缓存 access token
        keeper.setex(key, expires_in, value)

        # 缓存 refresh token
        refresh_key = u"refresh_%s_authorizer_refresh_token" % auth_info[u'authorizer_appid']
        refresh_value = auth_info[u'authorizer_refresh_token']

        keeper.set(refresh_key, refresh_value)

        return HttpResponse(u"ret: %r" % ret)
