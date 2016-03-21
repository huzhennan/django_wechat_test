# coding=utf-8
from django.http import HttpResponse

from . import Client


class WeResponse(object):
    @staticmethod
    def check_signature(request):
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')

        # TODO: 测试这里检查不通过, do something.
        if Client().check_signature(signature, timestamp, nonce):
            print 'success'
        else:
            print 'something is wrong'
        return HttpResponse(echostr)