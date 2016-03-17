# coding=utf-8
import requests
from wechat_sdk.exceptions import OfficialAPIError


def get(url, params=None, **kwargs):
    req = requests.get(url, params, **kwargs)

    req.raise_for_status()

    try:
        response_json = req.json()
    except ValueError:
        return req

    _check_official_error(response_json)

    return response_json


def post(url, data=None, json=None, **kwargs):
    req = requests.post(url, data=data, json=json, **kwargs)

    req.raise_for_status()

    try:
        response_json = req.json()
    except ValueError:
        return req

    _check_official_error(response_json)

    return response_json


def _check_official_error(json_data):
    """
    检测微信公众平台返回值中是否包含错误的返回码
    :raises OfficialAPIError: 如果返回码提示有错误，抛出异常；否则返回 True
    """
    if 'errcode' in json_data and json_data['errcode'] != 0:
        raise OfficialAPIError(errcode=json_data.get('errcode'), errmsg=json_data.get('errmsg', ''))
