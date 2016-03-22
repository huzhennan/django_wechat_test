# encoding=utf-8

from .conf import *
from .we import WeClient
from .we3rd import We3rdClient


def wechat_client():
    c = WeClient(APP_ID, APP_SECRET, TOKEN, store=store)
    return c


def wechat3rd_client(client_app_id=None):
    c = We3rdClient(component_app_id=COMPONENT_APP_ID,
                    component_app_secret=COMPONENT_APP_SECRET,
                    app_token=COMPONENT_TOKEN,
                    encoding_aes_key=COMPONENT_SYMMETRIC_KEY,
                    store=store,
                    client_app_id=client_app_id)
    return c
