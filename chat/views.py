# encoding=utf-8

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from wechat_sdk.exceptions import OfficialAPIError
from django.views.decorators.http import require_GET, require_POST

from chat import core
from chat.core3rd import client3rd
from .handles import generate_test_menu, get_open_id

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'chat/index.html', {})


def generate_menu(request):
    logger.debug("generate_menu 1111")
    client = core.client()
    try:
        redirect_url = request.POST.get('redirect_url')
        if redirect_url:
            generate_test_menu(client, redirect_url)
        else:
            generate_test_menu(client)
        messages.info(request, u'增加菜单成功')
    except OfficialAPIError:
        logger.exception("what wrong???")
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


@require_GET
def test_web_3rd(request):
    return render(request, 'chat/test_web_3rd.html')


def verify_ticket(request):
    if request.method == 'GET':
        client = client3rd()
        try:
            ticket = client.verify_ticket
        except RuntimeError as e:
            msg = u"我没有票,没有票"
            logger.exception(msg)
            ticket = msg
        return render(request, 'chat/verify_ticket.html', {'ticket': ticket})
    elif request.method == 'POST':
        ticket = request.POST.get('verify_ticket')

        client = client3rd()
        client.verify_ticket = ticket

        return render(request, 'chat/verify_ticket.html', {'ticket': ticket})


def component_token(request):
    if request.method == 'GET':
        return render(request, 'chat/component_token.html')
    elif request.method == 'POST':
        client = client3rd()
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
        client = client3rd()
        ret = client.get_pre_auth_code()
        logger.debug("ret: %r", ret)
        return render(request, 'chat/pre_auth_code.html', {'pre_auth_code': ret})


@require_GET
def component_login_page(request):
    client = client3rd()

    login_page_uri = client.generate_component_login_page(u"http://www.zaihuiba.com/chat/event_handler/")
    logger.debug("ret: %r", login_page_uri)
    return render(request, 'chat/component_login_page.html', {u'login_page_uri': login_page_uri})


def auth_token(request):
    if request.method == 'GET':
        return render(request, 'chat/auth_token.html')
    elif request.method == 'POST':
        appid = request.POST.get('appid')
        use_cache = request.POST.get('use_cache')

        client = client3rd()

        if use_cache == u'yes':
            ret = client.get_authorizer_token(appid)
        else:
            ret = client.api_authorizer_token(appid)

        return HttpResponse("ret:%r" % ret)


def web_3rd_operation(request):
    if request.method == 'GET':
        return render(request, 'chat/web_3rd_operation.html')
    elif request.method == 'POST':
        redirect_url = 'http://www.baidu.com'
        client = client3rd()

        try:
            generate_test_menu(client, redirect_url)
            messages.info(request, u'增加菜单成功')
        except OfficialAPIError:
            logger.exception("what wrong???")
            messages.error(request, u'Something wrong')

        return render(request, 'chat/web_3rd_operation.html')
