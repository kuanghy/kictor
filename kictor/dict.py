# -*- coding: utf-8 -*-

# Copyright (c) Huoty, All rights reserved
# Author: Huoty <sudohuoty@163.com>
# CreateTime: 2023-07-23 10:17:09

from __future__ import print_function

import time
import uuid
import json
import random
import platform
from importlib import import_module
from subprocess import Popen, call
try:
    from distutils.spawn import find_executable
except ImportError:
    find_executable = lambda name: name

from .config import config as cfg
from .util import iteritems, request, md5sum, sha256sum, contains_chinese
from .util import colorizing as _c


class BaseDict(object):

    def query(self, text):
        raise NotImplementedError()

    def show_result(sef, data):
        raise NotImplementedError()

    def show_no_result(self):
        print(_c(' -- No result for this query.', 'red'))

    def read_word(self, text):
        sys_name = platform.system()
        if 'Darwin' == sys_name:
            call(['say', text])
        elif 'Linux' == sys_name:
            if find_executable('festival'):
                Popen('echo ' + text + ' | festival --tts', shell=True)
            else:
                print(_c(' -- Please Install festival.', 'red'))
        else:
            print(_c(' -- Failed to read out the word.', 'red'))

    def query_and_show(self, text, read=False):
        data = self.query(text)
        self.show_result(data)
        if read:
            self.read_word(text)


class YoudaoDict(BaseDict):

    @staticmethod
    def _is_single_word(text):
        return " " not in text and "\t" not in text and "\n" not in text

    def query(self, text):
        api = cfg.get('youdao', 'api')
        app_key = cfg.get('youdao', 'app_key')
        app_secret = cfg.get('youdao', 'app_secret')
        salt = str(uuid.uuid1())
        curtime = str(int(time.time()))
        text_len = len(text)
        if text_len <= 20:
            input = text
        else:
            input = text[0:10] + str(text_len) + text[-10:]
        sign = sha256sum(app_key + input + salt + curtime + app_secret)
        data = {
            'q': text,
            'from': 'auto',
            'to': 'auto',
            'appKey': app_key,
            'salt': salt,
            'curtime': curtime,
            'signType': 'v3',
            'sign': sign
        }
        resp = request(api, data=data, method="POST")
        data = json.loads(resp)

        data.pop("dict", None)
        webdict = data.pop("webdict", {})
        if 'basic' not in data and webdict and 'url' in webdict:
            url = webdict['url']
            if contains_chinese(text):
                if self._is_single_word(text) and len(text) <= 6:
                    data["webdict"] = self.parse_webdict_zh(url)
            else:
                if len(text) <= 15 or self._is_single_word(text):
                    data["webdict"] = self.parse_webdict_en(url)

        return data

    def parse_webdict_en(self, url):
        try:
            lxml_html = import_module("lxml.html")
        except ImportError:
            return {}
        html_content = request(url)
        doc = lxml_html.fromstring(html_content)
        uk_phonetic_contents = doc.xpath(
            "//div[@id='ec']//span[contains(., '英')]/text() | "
            "//div[@id='ec']//span[contains(., '英')]/span[@class='phonetic']/text()"
        )
        uk_phonetic = ''.join([item.strip() for item in uk_phonetic_contents])
        us_phonetic_contents = doc.xpath(
            "//div[@id='ec']//span[contains(., '美')]/text() | "
            "//div[@id='ec']//span[contains(., '美')]/span[@class='phonetic']/text()"
        )
        us_phonetic = ''.join([item.strip() for item in us_phonetic_contents])
        phonetics = [item for item in [uk_phonetic, us_phonetic] if item]
        explains = doc.xpath('//div[@id="ec"]/ul/li/text()')
        wfs = doc.xpath('//div[@id="ec"]/div[@class="sub"]/p/text()')
        return {
            "phonetics": phonetics,
            "explains": explains,
            "wfs": wfs,
        }

    def parse_webdict_zh(self, url):
        try:
            lxml_html = import_module("lxml.html")
        except ImportError:
            return {}
        html_content = request(url)
        doc = lxml_html.fromstring(html_content)
        phonetics = doc.xpath("//div[@id='ce']//span[@class='phonetic']/text()")
        explains = doc.xpath("//div[@id='ce']/ul/a/text()")
        return {
            "phonetics": phonetics,
            "explains": explains,
        }

    def show_result(self, data):
        _d = data
        if not _d:
            self.show_no_result()
            return

        error_code = _d.get('errorCode')
        if error_code and error_code != '0':
            msg = {
                "102": "不支持的语言类型",
                "103": "翻译文本过长",
                "108": ("应用ID无效，注册账号，登录后台创建应用并完成绑定，"
                        "可获得应用ID和应用密钥等信息"),
                "113": "查询字段不能为空",
                "202": "签名检验失败",
                "401": "账户已经欠费，请进行账户充值",
                "412": "访问频率受限,请稍后访问",
            }.get(error_code, "ErrorCode: {}".format(error_code))
            print(_c(msg, 'red'))
            return

        print(_c(_d['query'], 'bold'), end='')

        if 'basic' in _d:
            _b = _d['basic']

            try:
                if 'uk-phonetic' in _b and 'us-phonetic' in _b:
                    print(" UK: [{0}]".format(_c(_b['uk-phonetic'], 'yellow')), end=',')
                    print(" US: [{0}]".format(_c(_b['us-phonetic'], 'yellow')))
                elif 'phonetic' in _b:
                    print(" [{0}]".format(_c(_b['phonetic'], 'yellow')))
                else:
                    print()
            except UnicodeEncodeError:
                print(" [ ---- ] ")

            if 'explains' in _b:
                print(_c('  词典释义:', 'cyan'))
                print(*map("     * {0}".format, _b['explains']), sep='\n')
            else:
                print()

            # Web reference
            if 'web' in _d:
                print(_c('\n  网络释义:', 'cyan'))
                print(*[
                    '     * {0}\n       {1}'.format(
                        _c(ref['key'], 'yellow'),
                        '; '.join(map(_c('{0}', 'magenta').format, ref['value']))
                    ) for ref in _d['web']], sep='\n')

            # 单词时态
            if "wfs" in _b:
                print(_c('\n  单词时态:', 'cyan'))
                wf_count = 0
                for wf in _b['wfs']:
                    wf = wf.get('wf', {})
                    name = wf.get('name')
                    value = wf.get('value')
                    if not name or not value:
                        continue
                    print("     * {0}: {1}".format(_c(name, "green"), value))
                    wf_count += 1
                if wf_count == 0:
                    print(_c('    -- No tense for this query.', 'red'))
        elif "webdict" in _d and _d["webdict"].get('explains'):
            webdict = _d["webdict"]
            phonetics = webdict.get('phonetics')
            if phonetics:
                print(_c('\n  音标拼音:', 'cyan'))
                print(*map("     * {0}".format, phonetics), sep='\n')
            explains = webdict['explains']
            if explains:
                print(_c('\n  基本释义:', 'cyan'))
                print(*map("     * {0}".format, explains), sep='\n')
            wfs = webdict.get('wfs')
            if wfs:
                print(_c('\n  单词时态:', 'cyan'))
                print(*map("     * {0}".format, wfs), sep='\n')
        elif 'translation' in _d:
            print(_c('\n  翻译结果:', 'cyan'))
            print(*map("     * {0}".format, _d['translation']), sep='\n')
        else:
            self.show_no_result()


class BaiduDict(BaseDict):

    def query(self, text):
        api = cfg.get('baidu', 'api')
        app_id = cfg.get('baidu', 'app_id')
        app_secret = cfg.get('baidu', 'app_secret')
        q_to = 'en' if contains_chinese(text) else 'zh'
        salt = str(random.randint(10000, 65536))
        sign = md5sum(app_id + text + salt + app_secret)
        data = {
            "appid": app_id,  # APP ID
            "q": text,
            "from": 'auto',  # 翻译源语言
            "to": q_to,  # 翻译目标语言
            "salt": salt,
            "sign": sign
        }
        resp = request(api, data=data, method="POST")
        return json.loads(resp)

    def show_result(self, data):
        if not data:
            self.show_no_result()
            return

        error_code = data.get('error_code')
        if error_code and error_code != '52000':
            msg = data.get('error_msg', "ErrorCode: {}".format(error_code))
            print(_c(msg, 'red'))
            return

        if "trans_result" in data:
            trans_result = data["trans_result"][0]
            print(_c(trans_result["src"], 'bold'))
            print(_c("  翻译结果:", 'cyan'))
            print(_c("     * {0}".format(trans_result["dst"]), 'magenta'))
        else:
            self.show_no_result()


class IcibaDict(BaseDict):

    def query(self, text):
        # 金山词霸开放接口
        api = cfg.get('iciba', 'api')
        key = cfg.get('iciba', 'key')
        params = {
            "w": text.lower(),  # 单词/汉字
            "type": "json",           # 返回格式 为空是xml 传入 xml 或者 json
            "key": key,               # 您申请到的key
        }
        resp = request(api, params=params, method="GET")
        return json.loads(resp)

    def show_result(self, data):
        _d = data
        if not _d:
            self.show_no_result()
            return

        print(_c(_d.get('word_name', ''), 'bold'), end='')

        symbols = _d["symbols"][0]
        if "parts" in symbols:
            if symbols.get("ph_en") and symbols.get("ph_am"):
                # 英式发音
                print(" UK: [{0}]".format(_c(symbols["ph_en"], 'yellow')), end=',')
                # 美式发音
                print(" US: [{0}]".format(_c(symbols["ph_am"], 'yellow')))
            elif symbols.get('ph_other'):
                print(" [{0}]".format(_c(symbols['ph_other'], 'yellow')))
            elif symbols.get('word_symbol'):
                print(" [{0}]".format(_c(symbols['word_symbol'], 'yellow')))
            else:
                print()

            parts = symbols["parts"]
            print(_c('  词典释义:', 'cyan'))
            for part in parts:
                means = part.get('means')
                if not means:
                    continue
                if isinstance(means[0], dict):
                    means = [mean.get("word_mean") for mean in means
                             if mean.get("word_mean")]
                    print(*map("    * {0}".format, means), sep='\n')
                else:
                    print('     * {0}\n       {1}'.format(
                        _c(part['part'], 'yellow'),
                        '; '.join(map(str, means))
                    ))

            if "exchange" in _d:
                print(_c('\n  单词时态:', 'cyan'))
                exchange_count = 0
                for wf_name, wf_value in iteritems(_d["exchange"]):
                    if not wf_value:
                        continue
                    if isinstance(wf_value, list):
                        wf_value = ", ".join(wf_value)
                    print("     * {0}: {1}".format(
                        _c(wf_name.split('_')[-1], "green"),
                        wf_value,
                    ))
                    exchange_count += 1
                if exchange_count == 0:
                    print(_c('    -- No tense for this query.', 'red'))
        else:
            self.show_no_result()
