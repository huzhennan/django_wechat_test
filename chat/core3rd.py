# encoding=utf-8
import logging
from urllib import urlencode

import redis
import requests as http
from django.http import HttpResponse
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

    def get_pre_auth_code(self):
        keeper = Keeper(self.store,
                        gain_func=self._gain_pre_auth_code)
        return keeper.get(Web3rdAuthMixin.PRE_AUTH_CODE_KEY)

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
        return keeper.get(Web3rdAuthMixin.COMPONENT_ACCESS_TOKEN_KEY)

    def _gain_component_access_token(self):
        url = u"https://api.weixin.qq.com/cgi-bin/component/api_component_token"
        data = {
            u"component_appid": self.app_id,
            u"component_appsecret": self.app_secret,
            u"component_verify_ticket": self.verify_ticket
        }
        logging.info("data: %r", data)
        return http.post(url, json=data).json()

    @property
    def verify_ticket(self):
        # return u'ticket@@@Vj2tT4I8R0vlyHTGNqDGSo7Dxvr6vYtHKF52yxcGuAFh0pOPh8A7OVf36uUpgDGrLY0WyZMDmolcihAeOgsrvw'
        keeper = Keeper(self.store)
        return keeper.get(Web3rdAuthMixin.COMPONENT_VERIFY_TICKET_KEY)

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
    def receive_verify_ticket(request):
        msg_signature = request.GET.get('msg_signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        client = client3rd()
        client.parse_data(data=request.body, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
        msg = client.get_message()

        verify_ticket = msg.ComponentVerifyTicket
        expires_in = 10 * 60

        client.store.setex(We3rdClient.COMPONENT_VERIFY_TICKET_KEY, expires_in, verify_ticket)
        logger.info("I gains a  ticket: %r, expires_in: %r", verify_ticket, expires_in)
        return HttpResponse(u"success")
