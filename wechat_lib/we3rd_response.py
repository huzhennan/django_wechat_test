# coding=utf-8
import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from wechat_lib import Client3rd
from wechat_lib.keeper import Keeper
from wechat_lib.we3rd import COMPONENT_VERIFY_TICKET_KEY, AUTH_ACCESS_TOKE_KEY, REFRESH_ACCESS_TOKE_KEY

logger = logging.getLogger(__name__)


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
        client = Client3rd()
        client.parse_data(data=request.body, msg_signature=msg_signature, timestamp=timestamp, nonce=nonce)
        msg = client.get_message()

        verify_ticket = msg.ComponentVerifyTicket
        expires_in = 10 * 60

        keeper = Keeper(client.store)
        keeper.setex(COMPONENT_VERIFY_TICKET_KEY, expires_in, verify_ticket)

        logger.info("I gains a  ticket: %r, expires_in: %r", verify_ticket, expires_in)
        return HttpResponse(u"success")

    @staticmethod
    def auth_handle(request, auth_code, expires_in):
        client = Client3rd()
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
