# encoding=utf-8
import logging
from urllib import urlencode

import redis
import requests as http
from datetime import datetime
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatConf, WechatBasic
from wechat_sdk.exceptions import ParseError, NeedParseError
from wechat_sdk.lib.parser import XMLStore
from wechat_sdk.messages import MESSAGE_TYPES, UnknownMessage

from chat.keeper import Keeper
from chat.utils import generate_url

logger = logging.getLogger(__name__)

APP_ID = u'wx67c082d3d5c5c355'
APP_SECRET = u'7678827bbe43445e4fb6631cd96e02dc'
TOKEN = u'ZaiHuiNiuBi20151102'
SYMMETRIC_KEY = u'yBUilBquwak6qAzuL1U04JrFSjwDjukjDoFjPRuLCU2'

CLIENT_APP_ID = u'wxd1ac16e44122c49a'

EXPIRES_AT = (datetime(2999, 1, 1) - datetime(1970, 1, 1)).total_seconds()

store = redis.StrictRedis(host='localhost', port=6379)


def client3rd(client_app_id=None):
    c = We3rdClient(component_app_id=APP_ID,
                    component_app_secret=APP_SECRET,
                    app_token=TOKEN,
                    encoding_aes_key=SYMMETRIC_KEY,
                    store=store,
                    client_app_id=client_app_id)
    return c


AUTH_ACCESS_TOKE_KEY = u"auth_%s_access_token"
REFRESH_ACCESS_TOKE_KEY = u"refresh_%s_access_token"


class We3rdAuthMixin(object):
    COMPONENT_VERIFY_TICKET_KEY = u"component_verify_ticket"
    COMPONENT_ACCESS_TOKEN_KEY = u"component_access_token"
    PRE_AUTH_CODE_KEY = u"pre_auth_code"

    def get_component_access_token(self):
        """
        2、获取第三方平台component_access_token
        :return:
        """
        keeper = Keeper(self.store,
                        gain_func=self.component_access_token,
                        shorten=60 * 10)
        ret = keeper.get(We3rdAuthMixin.COMPONENT_ACCESS_TOKEN_KEY)
        return ret.get(u'component_access_token')

    def get_pre_auth_code(self):
        """
        3、获取预授权码pre_auth_code
        :return:
        """
        keeper = Keeper(self.store,
                        gain_func=self.pre_auth_code)
        ret = keeper.get(We3rdAuthMixin.PRE_AUTH_CODE_KEY)
        return ret.get(u'pre_auth_code')

    def generate_component_login_page(self, redirect_uri):
        """
        对应 4、使用授权码换取公众号的接口调用凭据和授权信息
        生成weixin授权地址
        :param redirect_uri:
        :return:
        """
        params = (
            (u'component_appid', self.component_app_id),
            (u'pre_auth_code', self.get_pre_auth_code()),
            (u'redirect_uri', redirect_uri)
        )
        return generate_url(u'https://mp.weixin.qq.com/cgi-bin/componentloginpage', params=params)

    def api_query_auth(self, auth_code):
        """
        4、使用授权码换取公众号的接口调用凭据和授权信息
        该API用于使用授权码换取授权公众号的授权信息，并换取authorizer_access_token和authorizer_refresh_token
        :param auth_code:
        :return:
        """
        params = (
            (u"component_access_token", self.get_component_access_token()),
        )
        url = generate_url(u"https://api.weixin.qq.com/cgi-bin/component/api_query_auth", params=params)
        data = {
            u"component_appid": self.component_app_id,
            u"authorization_code": auth_code
        }
        return http.post(url, json=data).json()

    def api_authorizer_token(self):
        """
        5、获取（刷新）授权公众号的接口调用凭据（令牌）
        :return:
        """
        params = (
            (u"component_access_token", self.get_component_access_token()),
        )
        url = generate_url(u"https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token", params=params)
        data = {
            u"component_appid": self.component_app_id,
            u"authorizer_appid": self.client_app_id,
            u"authorizer_refresh_token": self._refresh_token()
        }
        return http.post(url, json=data).json()

    def get_authorizer_token(self):
        keeper = Keeper(self.store,
                        gain_func=self.api_authorizer_token)
        key = AUTH_ACCESS_TOKE_KEY % self.client_app_id
        return keeper.get(key)

    def pre_auth_code(self):
        token = self.get_component_access_token()
        params = {
            u'component_access_token': token
        }
        url = generate_url(u"https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode", params)

        json_data = {
            u"component_appid": self.component_app_id
        }
        return http.post(url, json=json_data).json()

    def component_access_token(self):
        url = u"https://api.weixin.qq.com/cgi-bin/component/api_component_token"
        data = {
            u"component_appid": self.component_app_id,
            u"component_appsecret": self.component_app_secret,
            u"component_verify_ticket": self.verify_ticket
        }
        logging.info("data: %r", data)
        return http.post(url, json=data).json()

    def _refresh_token(self):
        keeper = Keeper(self.store)
        key = REFRESH_ACCESS_TOKE_KEY % self.client_app_id
        return keeper.get(key)

    @property
    def verify_ticket(self):
        keeper = Keeper(self.store)
        return keeper.get(We3rdAuthMixin.COMPONENT_VERIFY_TICKET_KEY)

    @verify_ticket.setter
    def verify_ticket(self, ticket):
        keeper = Keeper(self.store)
        keeper.setex(We3rdAuthMixin.COMPONENT_VERIFY_TICKET_KEY, 60 * 10, ticket)

    @property
    def store(self):
        raise NotImplementedError()

    @property
    def component_app_id(self):
        raise NotImplementedError()

    @property
    def component_app_secret(self):
        raise NotImplementedError()

    @property
    def client_app_id(self):
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


class Web3rdAuthMixin(object):
    def get_web_token(self, code):
        url = u"https://api.weixin.qq.com/sns/oauth2/component/access_token"
        params = (
            ('appid', self.client_app_id),
            ('code', code),
            ('grant_type', 'authorization_code'),
            ('component_appid', self.component_app_id),
            ('component_access_token', self.component_app_secret)
        )
        ret = http.get(url, params=params)
        return ret.json()

    def get_open_id(self, code):
        return self.get_web_token(code)[u'openid']

    @property
    def component_app_id(self):
        raise NotImplementedError()

    @property
    def component_app_secret(self):
        raise NotImplementedError()

    @property
    def client_app_id(self):
        raise NotImplementedError()


class We3rdClient(RewriteMixin, WechatBasic, We3rdAuthMixin, Web3rdAuthMixin):
    def __init__(self, component_app_id, component_app_secret,
                 app_token, encoding_aes_key, store, encrypt_mode='safe', client_app_id=None):
        conf = WechatConf(
            appid=component_app_id,
            appsecret=component_app_secret,
            token=app_token,
            encrypt_mode=encrypt_mode,
            encoding_aes_key=encoding_aes_key,
            access_token_getfunc=self.token_get_func
        )
        WechatBasic.__init__(self, conf=conf)
        self.__component_app_id = component_app_id
        self.__component_app_secret = component_app_secret
        self.__store = store
        self.__client_app_id = client_app_id

    def token_get_func(self):
        ret = self.get_authorizer_token()
        return ret[u'authorizer_access_token'], EXPIRES_AT

    @property
    def store(self):
        return self.__store

    @property
    def component_app_id(self):
        return self.__component_app_id

    @property
    def component_app_secret(self):
        return self.__component_app_secret

    @property
    def client_app_id(self):
        return self.__client_app_id


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
        """
        响应 1、推送component_verify_ticket
        :param request:
        :param msg_signature:
        :param timestamp:
        :param nonce:
        :return:
        """
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

        key = AUTH_ACCESS_TOKE_KEY % auth_info[u'authorizer_appid']
        # 缓存 access token
        keeper.setex(key, expires_in, auth_info)

        # 缓存 refresh token
        refresh_key = REFRESH_ACCESS_TOKE_KEY % auth_info[u'authorizer_appid']
        refresh_value = auth_info[u'authorizer_refresh_token']

        keeper.set(refresh_key, refresh_value)

        messages.add_message(request, messages.INFO, "获取授权成功")
        return HttpResponseRedirect(reverse('home'))
