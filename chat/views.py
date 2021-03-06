# encoding=utf-8

import logging

import time
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from wechat_sdk.exceptions import OfficialAPIError
from django.views.decorators.http import require_GET, require_POST

from wechat_lib.store_key import AUTH_ACCESS_TOKE_KEY
from .handles import generate_test_menu, get_open_id
from wechat_lib import wechat_client, wechat3rd_client

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def generate_menu(request):
    if request.method == 'GET':
        return render(request, 'chat/generate_menu.html', {})
    elif request.method == 'POST':
        logger.debug("generate_menu 1111")
        cli = wechat_client()
        try:
            redirect_url = request.POST.get('redirect_url')
            if redirect_url:
                generate_test_menu(cli, cli.app_id, redirect_url)
            else:
                generate_test_menu(cli, cli.app_id)
            messages.info(request, u'增加菜单成功')
        except OfficialAPIError:
            logger.exception("what wrong???")
            messages.error(request, u'Something wrong')

        logger.debug("ret: %r", cli.get_menu())

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


@require_GET
def test_web_3rd(request):
    code = request.GET.get('code')
    appid = request.GET.get('appid')
    if code is not None and appid is not None:
        client = wechat3rd_client(client_app_id=appid)
        # ret = client.get_web_token(code)
        open_id = client.get_open_id(code)
        logger.debug('test_web_3rd ret: %r', open_id)
        return render(request, 'chat/test_web_3rd.html', {'open_id': open_id})

    return render(request, 'chat/test_web_3rd.html')


def verify_ticket(request):
    if request.method == 'GET':
        client = wechat3rd_client()
        try:
            ticket = client.verify_ticket
        except RuntimeError as e:
            msg = u"我没有票,没有票"
            logger.exception(msg)
            ticket = msg
        return render(request, 'chat/verify_ticket.html', {'ticket': ticket})
    elif request.method == 'POST':
        ticket = request.POST.get('verify_ticket')

        client = wechat3rd_client()
        client.verify_ticket = ticket

        return render(request, 'chat/verify_ticket.html', {'ticket': ticket})


def component_token(request):
    if request.method == 'GET':
        return render(request, 'chat/component_token.html')
    elif request.method == 'POST':
        client = wechat3rd_client()
        try:
            ret = client.get_component_access_token()
        except RuntimeError, e:
            logging.error(e.message)
            ret = "ERROR"
        return render(request, 'chat/component_token.html', {'component_access_token': ret})


def pre_auth_code(request):
    if request.method == 'GET':
        return render(request, 'chat/pre_auth_code.html')
    elif request.method == 'POST':
        client = wechat3rd_client()
        ret = client.get_pre_auth_code()
        logger.debug("ret: %r", ret)
        return render(request, 'chat/pre_auth_code.html', {'pre_auth_code': ret})


@require_GET
def component_login_page(request):
    client = wechat3rd_client()

    login_page_uri = client.generate_component_login_page(u"http://www.zaihuiba.com/chat/event_handler/")
    logger.debug("ret: %r", login_page_uri)
    return render(request, 'chat/component_login_page.html', {u'login_page_uri': login_page_uri})


def auth_token(request):
    if request.method == 'GET':
        return render(request, 'chat/auth_token.html')
    elif request.method == 'POST':
        appid = request.POST.get('appid')
        use_cache = request.POST.get('use_cache')

        client = wechat3rd_client(client_app_id=appid)

        if use_cache != u'yes':
            key = AUTH_ACCESS_TOKE_KEY % client.client_app_id
            client.store.delete(key)

        ret = client.get_authorizer_token()

        return HttpResponse("ret:%r" % ret)


def web_3rd_operation(request):
    if request.method == 'GET':
        return render(request, 'chat/web_3rd_operation.html')
    elif request.method == 'POST':
        redirect_url = request.POST.get('redirect_url')
        appid = request.POST.get('appid')
        client = wechat3rd_client(client_app_id=appid)

        logger.debug("before menu: %r", client.get_menu())

        try:
            generate_test_menu(client, client.client_app_id,
                               redirect_url=redirect_url,
                               component_appid=client.component_app_id)
            messages.info(request, u'增加菜单成功')
        except OfficialAPIError:
            logger.exception("what wrong???")
            messages.error(request, u'Something wrong')

        logger.debug("before menu: %r", client.get_menu())

        return render(request, 'chat/web_3rd_operation.html')


def home(request):
    return render(request, 'chat/home.html')
