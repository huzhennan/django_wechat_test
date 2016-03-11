# encoding=utf-8

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk.exceptions import OfficialAPIError
from wechat_sdk.lib.crypto import BasicCrypto

from .handles import generate_test_menu, get_open_id

import logging

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'chat/index.html', {})


def generate_menu(request):
    logger.debug("generate_menu 1111")
    try:
        redirect_url = request.POST.get('redirect_url')
        if redirect_url:
            generate_test_menu(redirect_url)
        else:
            generate_test_menu()
        messages.info(request, u'增加菜单成功')
    except OfficialAPIError, e:
        print e
        messages.error(request, u'Something wrong')

    return HttpResponseRedirect(reverse('chat:index'))


def open_id(request):
    code = request.GET.get('code')
    open_id = get_open_id(code)

    return render(request,
                  'chat/open_id.html',
                  {
                      'code': code,
                      'open_id': open_id
                  })


TOKEN = u'ZaiHuiNiuBi20151102'
SYMMETRIC_KEY = u'yBUilBquwak6qAzuL1U04JrFSjwDjukjDoFjPRuLCU2'
APP_ID = u'wx67c082d3d5c5c355'


@csrf_exempt
def receive_verify_ticket(request):
    msg_signature = request.GET.get('msg_signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')

    crypto = BasicCrypto(TOKEN, SYMMETRIC_KEY, APP_ID)
    msg = crypto.decrypt_message(msg=request.body, msg_signature=msg_signature, nonce=nonce, timestamp=timestamp)



    logger.info("msg: %r", msg)
    return HttpResponse(u"success")
