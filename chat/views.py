# encoding=utf-8

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from wechat_sdk.exceptions import OfficialAPIError

from .handles import generate_menu_handle


def index(request):
    return render(request, 'index.html', {})


def generate_menu(request):
    try:
        generate_menu_handle()
        messages.info(request, u'增加菜单成功')
    except OfficialAPIError, e:
        print e
        messages.error(request, u'Something wrong')

    return HttpResponseRedirect(reverse('chat:index'))
