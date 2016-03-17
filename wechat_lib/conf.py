# encoding=utf-8


from datetime import datetime

import redis

store = redis.StrictRedis(host='localhost', port=6379)

# 微信公众号的配置信息
TOKEN = u"ZaiHuiWanSui2015"
APP_ID = u"wxd1ac16e44122c49a"
APP_SECRET = u"d3ddce902a9d3c1f2071eb25f479df33"

# 微信第三方的配置信息
COMPONENT_APP_ID = u'wx67c082d3d5c5c355'
COMPONENT_APP_SECRET = u'7678827bbe43445e4fb6631cd96e02dc'
COMPONENT_TOKEN = u'ZaiHuiNiuBi20151102'
COMPONENT_SYMMETRIC_KEY = u'yBUilBquwak6qAzuL1U04JrFSjwDjukjDoFjPRuLCU2'

# access_token_getfunc 需要返回形如(token, expires_at)的数据
# 可我们并不需要这个过期时间,由store存储管理
# 给一个未来的时间
EXPIRES_AT = (datetime(2999, 1, 1) - datetime(1970, 1, 1)).total_seconds()
