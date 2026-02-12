# -*- coding: utf-8 -*-

# Copyright (c) Huoty, All rights reserved
# Author: Huoty <sudohuoty@163.com>
# CreateTime: 2023-07-23 10:15:03

import sys
import re
import time
import socket
import hashlib
from json import dumps as json_dumps
try:
    from urllib.request import urlopen, Request as HTTPRequest
    from urllib.parse import urlencode
    from urllib.error import URLError, HTTPError
except ImportError:
    from urllib2 import URLError, HTTPError, urlopen, Request as HTTPRequest
    from urllib import urlencode


def setdefaultencoding(encoding='utf-8'):
    if sys.version_info[0] >= 3:
        return

    stdin, stdout, stderr = sys.stdin, sys.stdout, sys.stderr
    reload(sys)  # noqa
    sys.setdefaultencoding(encoding)
    sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr


def iteritems(obj):
    try:
        return obj.iteritems()
    except AttributeError:
        return obj.items()


def contains_chinese(text):
    """判断是否包含中文"""
    for uchar in text:
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return True
    return False


def split_string_ignore_quotes(string):
    pattern = r'\s+(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)'
    return [
        item.replace('"', '').replace("'", "")
        for item in re.split(pattern, string)
    ]


def md5sum(data, encoding='utf-8'):
    data = data.encode(encoding)
    return hashlib.md5(data).hexdigest()


def sha256sum(data, encoding='utf-8'):
    data = data.encode(encoding)
    return hashlib.sha256(data).hexdigest()


class cached_property(object):

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def request(url, params=None, data=None, json=None, headers=None, method="GET",
            timeout=5):
    if params:
        url += "?" + urlencode(params)
    headers = headers or {}
    if data:
        data = urlencode(data).encode('utf-8')
    elif json:
        data = json_dumps(json, default=str).encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
    try:
        req = HTTPRequest(url, data=data, headers=headers, method=method)
    except TypeError:
        req = HTTPRequest(url, data=data, headers=headers)
    resp = None
    error = None
    retry_count = 5
    for idx in range(retry_count):
        try:
            resp = urlopen(req, timeout=timeout)
            resp_body = resp.read()
            resp_data = resp_body.decode("utf-8")

            status_code = resp.getcode()
            if status_code == 200:
                return resp_data
            elif status_code >= 500:
                raise HTTPError(
                    url, status_code, resp_data[:100], resp.headers, None
                )
            else:
                raise Exception("HTTP {}: {}".format(
                    status_code, resp_data[:100]
                ))
        except (URLError, HTTPError, OSError, socket.error) as ex:
            error = ex
            if idx < retry_count - 1:
                time.sleep(1)

    if error:
        raise error


class Colorizing(object):

    colors = {
        'none': "",
        'default': "\033[0m",
        'bold': "\033[1m",
        'underline': "\033[4m",
        'blink': "\033[5m",
        'reverse': "\033[7m",
        'concealed': "\033[8m",

        'black': "\033[30m",
        'red': "\033[31m",
        'green': "\033[32m",
        'yellow': "\033[33m",
        'blue': "\033[34m",
        'magenta': "\033[35m",
        'cyan': "\033[36m",
        'white': "\033[37m",

        'on_black': "\033[40m",
        'on_red': "\033[41m",
        'on_green': "\033[42m",
        'on_yellow': "\033[43m",
        'on_blue': "\033[44m",
        'on_magenta': "\033[45m",
        'on_cyan': "\033[46m",
        'on_white': "\033[47m",

        'beep': "\007",
    }

    disabled = False

    @cached_property
    def is_tty(self):
        isatty = getattr(sys.stdout, 'isatty', None)
        return isatty and isatty()

    def __call__(self, s, color='none'):
        if not self.disabled and self.is_tty and color in self.colors:
            return "{0}{1}{2}".format(
                self.colors[color],
                s,
                self.colors['default']
            )
        else:
            return s


colorizing = Colorizing()
