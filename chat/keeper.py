# coding=utf-8
from __future__ import absolute_import

import redis
import logging
import ast

logger = logging.getLogger(__name__)


class Keeper(object):
    EXPIRES_IN = u'expires_in'

    def __init__(self, store, key, gain_func=None, shorten=0):
        """
        :param store: redis存储
        :param key: 用来生成key
        :param gain_func: 从网上获取taken的方法
        :param shorten: 缩短`expires_in`大小
        """
        self.__store = store
        self.__key = key
        self.__gain_func = gain_func
        self.__shorten = shorten

    def get(self):
        var = self.store.get(self.key)
        if var:
            logger.debug("get %r = %r from store", self.key, var)
            return ast.literal_eval(var)
        else:
            if callable(self.gain_func):
                var = self.gain_func()
                logger.debug("get %r = %r from %r", self.key, var, self.gain_func)
                expires_in = var.get(Keeper.EXPIRES_IN, None)
                if expires_in:
                    expires_in = int(expires_in) - self.shorten

                if expires_in:
                    self.store.setex(self.key, expires_in, var)
                else:
                    self.store.set(self.key, var)
                return var
            else:
                raise RuntimeError("I need get a way to get value")

    def setex(self, name, value, time):
        """
        Set the value of key name to value that expires in time seconds
        """
        return self.store.setex(name, value, time)

    def set(self, name, value):
        """
        Set the value at key name to value
        """
        return self.set(name, value)

    @property
    def store(self):
        return self.__store

    @property
    def key(self):
        return self.__key

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
    keeper = Keeper(store, "access_token", obj.gain_func)

    print "%r %r" % ('haha', keeper.get())
