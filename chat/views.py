# encoding=utf-8

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from wechat_sdk.exceptions import OfficialAPIError
from django.views.decorators.http import require_GET, require_POST

from chat.core3rd import client3rd
from .handles import generate_test_menu, get_open_id

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


def test_web_3rd(request):
    if request.method == 'GET':
        return render(request, 'chat/test_web_3rd.html')
    elif request.method == 'POST':
        client = client3rd()
        try:
            ret = client.grant_component_access_token()
        except RuntimeError, e:
            logging.error(e.message)
            ret = "ERROR"

        return render(request, 'chat/test_web_3rd.html', {'component_access_token': ret})



