# encoding=utf-8
import logging

import redis
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatConf, WechatBasic
from wechat_sdk.lib.crypto import BasicCrypto

logger = logging.getLogger(__name__)

TOKEN = u'ZaiHuiNiuBi20151102'
SYMMETRIC_KEY = u'yBUilBquwak6qAzuL1U04JrFSjwDjukjDoFjPRuLCU2'
APP_ID = u'wx67c082d3d5c5c355'
APP_SECRET = u'7678827bbe43445e4fb6631cd96e02dc'

store = redis.StrictRedis(host='localhost', port=6379)


def client3rd():
    c = We3rdClient(APP_ID, APP_SECRET, TOKEN, SYMMETRIC_KEY, store=store)
    return c


class We3rdClient(WechatBasic):
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


class We3rdResponse(object):
    @staticmethod
    @csrf_exempt
    def receive_verify_ticket(request):
        msg_signature = request.GET.get('msg_signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        logger.info("before msg: %r", request.body)

        # crypto = BasicCrypto(TOKEN, SYMMETRIC_KEY, APP_ID)
        # msg = crypto.decrypt_message(msg=request.body, msg_signature=msg_signature, nonce=nonce, timestamp=timestamp)

        client = client3rd()
        client.parse_data(data=request.body, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
        msg = client.get_message()

        logger.info("msg: %r", msg)
        return HttpResponse(u"success")


class Web3rdClient(object):
    def pre_auth_code(self, component_appid):
        url = u"https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode"
