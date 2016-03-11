# coding=utf-8
from __future__ import absolute_import

import redis
import logging

logger = logging.getLogger(__name__)


class Keeper(object):
    def __init__(self, name, client, store):
        """
        :name 用来生成key
        :param client: 从网上获取taken的方法
        """
        self.__name = name
        self.__client = client
        self.__store = store

    def get_access_token(self):
        cell = self.store().get(self.key())
        logger.debug(self.store().ttl(self.key()))
        if cell:
            return cell
        else:
            logger.debug("Get token from request")
            json_ret = self.client().grant_token()
            token = json_ret[u'access_token']
            expires_in = int(json_ret[u'expires_in'])
            store.setex(self.key(), expires_in, token)

            return token

    def client(self):
        return self.__client

    def store(self):
        return self.__store

    def key(self):
        return self.__name


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from chat.core import client

    store = redis.StrictRedis(host='localhost', port=6379)
    c = client()
    keeper = Keeper("access_token", c, store)

    print keeper.get_access_token()
