# encoding=utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage, EventMessage

from wechat_lib import wechat_client

logger = logging.getLogger(__name__)


@csrf_exempt
def public_event_handle(request):
    """
    公众平台事件处理
    :return:
    """
    if request.method == 'GET':
        return _check_signature(request)
    elif request.method == 'POST':
        return _msg_handle(request)


def _check_signature(request):
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    echostr = request.GET.get('echostr')

    if wechat_client().check_signature(signature, timestamp, nonce):
        logger.debug('wechat check_signature success')
    else:
        logger.debug('wechat check_signature fail')
    return HttpResponse(echostr)


def _msg_handle(request):
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')

    client = wechat_client()
    try:
        client.parse_data(data=request.body,
                          msg_signature=signature,
                          timestamp=timestamp,
                          nonce=nonce)
    except ParseError as e:
        logger.exception("Error")

    if isinstance(client.message, TextMessage):
        return _text_msg_handle(request, client, client.message.content)
    elif isinstance(client.message, EventMessage):
        return _event_msg_handle(request, client)
    return HttpResponse("")


def _text_msg_handle(request, client, text):
    logger.debug("_text_msg_handle %r", text)
    response_content = client.response_text("hello, recevice: %r" % text)
    return HttpResponse(response_content)


def _event_msg_handle(request, client):
    logger.debug("_event_msg_handle: %r", client.message.type)
    return HttpResponse("")
