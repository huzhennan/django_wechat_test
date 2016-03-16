# coding=utf-8
from __future__ import absolute_import

import json
import unittest

import redis
from  redis.exceptions import ConnectionError

from chat.keeper import Keeper


class AMock(object):
    def gain_func(self):
        return {"key": "this is"}


class BMock(object):
    def gain_func(self, **kwargs):
        return {"key": "this is %r" % kwargs}


class TestKeeper(unittest.TestCase):
    KEY1 = "test_key"

    def setUp(self):
        try:
            self.store = redis.StrictRedis(host='localhost', port=6379)
            # 试图连接redis-server
            self.store.time()
            self.store.delete(TestKeeper.KEY1)
        except ConnectionError:
            raise RuntimeError("需要开启本地redis-server")

    def test_get_with_source(self):
        a = AMock()
        keeper = Keeper(self.store, a.gain_func)

        ret, source = keeper.get_with_source(TestKeeper.KEY1)
        self.assertIsInstance(ret, dict)
        self.assertDictEqual(ret, {"key": "this is"})
        self.assertEqual(source, "request")

        ret, source = keeper.get_with_source(TestKeeper.KEY1)
        self.assertEqual(source, "cache")

    def test_get(self):
        a = AMock()
        keeper = Keeper(self.store, a.gain_func)
        ret = keeper.get(TestKeeper.KEY1)
        self.assertDictEqual(ret, {"key": "this is"})

    def test_setex(self):
        keeper = Keeper(self.store)
        val = u"hello"
        keeper.setex(TestKeeper.KEY1, 1000, val)

        ret = self.store.get(TestKeeper.KEY1)

        self.assertEqual(json.loads(ret), val)

    def test_test(self):
        keeper = Keeper(self.store)
        val = u"world"
        keeper.set(TestKeeper.KEY1, val)

        ret = self.store.get(TestKeeper.KEY1)

        self.assertEqual(json.loads(ret), val)

    def test_get_with_args(self):
        b = BMock()
        keeper = Keeper(self.store, gain_func=b.gain_func, gain_args={'arg': '1'})
        ret = keeper.get(TestKeeper.KEY1)
        self.assertDictEqual(ret, {"key": "this is {'arg': '1'}"})

