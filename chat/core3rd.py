# encoding=utf-8
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

TOKEN = u'ZaiHuiNiuBi20151102'
SYMMETRIC_KEY = u'yBUilBquwak6qAzuL1U04JrFSjwDjukjDoFjPRuLCU2'
APP_ID = u'wx67c082d3d5c5c355'


class We3rdResponse(object):
    @staticmethod
    @csrf_exempt
    def receive_verify_ticket(request, app_id):
        logger.info("app_id: %r, body: %r", app_id,  request.body)
        return HttpResponse(u"success")


class Web3rdClient(object):
    def pre_auth_code(self, component_appid):
        url = u"https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode"
