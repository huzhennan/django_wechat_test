# coding=utf-8
from urllib import urlencode


def generate_url(base_url, params):
    return base_url + "?" + urlencode(params)


def generate_auth_url(app_id, redirect_uri, scope='snsapi_base', state='test', component_appid=None):
    """
    生成网页制授权页面(对应第一步:用户同意授权，获取code)
    :param redirect_uri: 授权后重定向的回调链接地址，请使用urlencode对链接进行处理
    :param scope: 应用授权作用域，snsapi_base （不弹出授权页面，直接跳转，只能获取用户openid）,
    snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。
    :param state: 重定向后会带上state参数，开发者可以填写a-zA-Z0-9的参数值，最多128字节
    :return:
    """
    params = [
        ('appid', app_id),
        ('redirect_uri', redirect_uri),
        ('response_type', 'code'),
        ('scope', scope),
        ('state', state)
    ]

    if component_appid is not None:
        params.append(['component_appid', component_appid])
    return generate_url('https://open.weixin.qq.com/connect/oauth2/authorize', params)
