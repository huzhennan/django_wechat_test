# coding=utf-8
from __future__ import absolute_import

import json
import logging

import redis

logger = logging.getLogger(__name__)


class Keeper(object):
    EXPIRES_IN = u'expires_in'

    def __init__(self, store, gain_func=None, shorten=0):
        """
        :param store: redis存储
        :param gain_func: 从网上获取taken的方法
        :param shorten: 缩短`expires_in`大小
        """
        self.__store = store
        self.__gain_func = gain_func
        self.__shorten = shorten

    def get(self, key):
        var = self.store.get(key)
        if var:
            var = json.loads(var)
            logger.debug("get %r = %r from store", key, var)
            return var
        else:
            if callable(self.gain_func):
                var = self.gain_func()
                logger.debug("get %r = %r from %r", key, var, self.gain_func)
                expires_in = var.get(Keeper.EXPIRES_IN, None)
                if expires_in:
                    expires_in = int(expires_in) - self.shorten

                var_json = json.dumps(var)
                if expires_in:
                    self.store.setex(key, expires_in, var_json)
                else:
                    self.store.set(key, var_json)
                return var
            else:
                raise RuntimeError("I need a way to get value(self.gain_func==null)")

    def setex(self, key, time, value):
        """
        Set the value of key name to value that expires in time seconds
        """
        val = json.dumps(value)
        return self.store.setex(key, time, val)

    def set(self, key, value):
        """
        Set the value at key name to value
        """
        val = json.dumps(value)
        return self.set(key, val)

    @property
    def store(self):
        return self.__store

    @property
    def gain_func(self):
        return self.__gain_func

    @property
    def shorten(self):
        return self.__shorten


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)


    class A(object):
        def gain_func(self):
            return {"key": "this is"}


    obj = A()
    store = redis.StrictRedis(host='localhost', port=6379)
    keeper = Keeper(store, obj.gain_func)

    ret = keeper.get("access_token")

    print "%r %r" % (type(ret), ret)

    keeper.setex("access_token2", 1000, "hello")
    ret2 = keeper.get("access_token2")
    print "%r %r" % (type(ret2), ret2)

