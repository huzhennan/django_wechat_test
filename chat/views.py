# encoding=utf-8

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from wechat_sdk.exceptions import OfficialAPIError

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
