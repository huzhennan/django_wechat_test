from __future__ import absolute_import

import unittest

import redis

from chat.core3rd import We3rdClient

APP_ID = u'wx67c082d3d5c5c355'
APP_SECRET = u'7678827bbe43445e4fb6631cd96e02dc'
TOKEN = u'ZaiHuiNiuBi20151102'
SYMMETRIC_KEY = u'yBUilBquwak6qAzuL1U04JrFSjwDjukjDoFjPRuLCU2'

CLIENT_APP_ID = u'wx003b0a1d1a2990ad'

store = redis.StrictRedis(host='localhost', port=6379)

class TestCore3rd(unittest.TestCase):

    def test_get_token(self):
        client = We3rdClient(APP_ID, APP_SECRET, TOKEN, SYMMETRIC_KEY,
                             store=store,
                             client_app_id=CLIENT_APP_ID)
        print client.get_access_token()