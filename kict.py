#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#     Filename @  kict.py
#       Author @  Huoty
#  Create date @  2016-04-10 09:18:02
#  Description @
# *************************************************************

from __future__ import unicode_literals
from __future__ import print_function

import sys
import hashlib
import random
import re
import requests
from argparse import ArgumentParser
from pprint import pprint

DEBUG = True

PY3 = sys.version_info >= (3, 0)

if not PY3:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

# youdao api
SELECT_YOUDAO = 0
YOUDAO_KEYFROM = "Kictor"
YOUDAO_API_KEY = "2047746926"

# baidu api
SELECT_BAIDU = 1
BAIDU_APP_ID = "20160409000018177"
BAIDU_SECRET_KEY = "qwJBEKy7dcychROiwMMk"

# iciba api
SELECT_ICIBA = 2
ICIBA_KEY = "F45625719E3AC2B588DE9B3807EDD1FF"

# iciba daysay api
DSAPI = "http://open.iciba.com/dsapi"

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

    @classmethod
    def colorize(cls, s, color=None):
        if color in cls.colors:
            return "{0}{1}{2}".format(
                cls.colors[color], s, cls.colors['default'])
        else:
            return s

class Dictor(object):

    def __init__(self, select_api):
        self.select_api = select_api
        self.trans_data = {}
        self.has_result = False
        self.debug = False
        self.__api_info = {}

    def set_trans_data(self, query):
        self.__store_api_info(query)
        url = self.__api_info["youdao"]["url"]
        payload = self.__api_info["youdao"]["payload"]
        if self.select_api:
            if self.select_api == SELECT_BAIDU:
                url = self.__api_info["baidu"]["url"]
                payload = self.__api_info["baidu"]["payload"]
            if self.select_api == SELECT_ICIBA:
                url = self.__api_info["iciba"]["url"]
                payload = self.__api_info["iciba"]["payload"]

        try:
            r = requests.get(url, params=payload, timeout=10)
            if self.debug: print("Request url: ", r.url)
        except requests.exceptions.Timeout:
            print("Connection timeout!")
        except requests.exceptions.ConnectionError:
            print("Connection error!")
        except requests.exceptions.HTTPError:
            print("Invalid HTTP response!")

        if r.status_code == requests.codes.ok:
            try:
                self.trans_data = r.json()
                if self.debug: pprint(self.trans_data)
            except Exception as e:
                print("Error: ", e)
        else:
            print("Request was aborted, status code is", r.status_code)

    def print_trans_result(self, refer=False, read=False):
        if self.select_api == SELECT_BAIDU:
            self.__baidu_trans_result(refer, read)
        elif self.select_api == SELECT_ICIBA:
            pass
        else:
            self.__youdao_trans_result()

        if not self.has_result:
            print(Colorizing.colorize(' -- No result for this query.', 'red'))

        print()

    def set_debuglevel(self, level):
        self.debug = level

    def __youdao_trans_result(self, refer=False, read=False):
        _c = Colorizing.colorize
        _d = self.trans_data

        print(_c(_d["query"], 'bold'), end='')

        if 'basic' in _d:
            self.has_result = True
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

            if 'speech' in _b:
                print(_c('  Text to Speech:', 'cyan'))
                if 'us-speech' in _b and 'uk-speech' in _b:
                    print("     * UK:", _b['uk-speech'])
                    print("     * US:", _b['us-speech'])
                elif 'speech' in _b:
                    print("     *", _b['speech'])
                print()

            if 'explains' in _b:
                print(_c('  词典释义:', 'cyan'))
                print(*map("     * {0}".format, _b['explains']), sep='\n')
            else:
                print()
        elif 'translation' in _d:
            self.has_result = True
            print(_c('\n  翻译结果:', 'cyan'))
            print(*map("     * {0}".format, _d['translation']), sep='\n')
        else:
            print()

        # Web reference
        if 'web' in _d:
            self.has_result = True
            print(_c('\n  网络释义:', 'cyan'))
            print(*[
                '     * {0}\n       {1}'.format(
                    _c(ref['key'], 'yellow'),
                    '; '.join(map(_c('{0}', 'magenta').format, ref['value']))
                ) for ref in web], sep='\n')

        # read out the word
        if options.read:
            sys_name = platform.system()
            if 'Darwin' == sys_name:
                call(['say', query])
            elif 'Linux' == sys_name:
                if spawn.find_executable('festival'):
                    Popen('echo ' + query + ' | festival --tts', shell=True)
                else:
                    print(_c(' -- Please Install festival.', 'red'))

    def __baidu_trans_result(self):
        _c = Colorizing.colorize
        if "trans_result" in self.trans_data:
            self.has_result = True
            trans_result = self.trans_data["trans_result"][0]
            print(_c(trans_result["src"], 'bold'))
            print(_c("翻译结果:", 'cyan'))
            print(_c("  * {0}".format(trans_result["dst"]), 'magenta'))

    def __iciba_trans_result(self):
        _c = Colorizing.colorize
        _d = self.trans_data

         print(_c(_d["word_name"], 'bold'), end='')

        if "exchange" in _d:
            tense = {}
            for t, w in _d["exchanges"].iteritems():
                if w:
                    tense[t.split('_')[1]] = ", ".join(w)

            symbols = _d["symbols"][0]
            if symbols.get("ph_en") and symbols.get("ph_em"):
                    print(" UK: [{0}]".format(_c(symbols["ph_en"], 'yellow')), end=',')  # 英式发音
                    print(" US: [{0}]".format(_c(symbols["ph_em"], 'yellow')))  # 美式发音
            elif symbols.get('ph_other'):
                print(" [{0}]".format(_c(symbols['ph_other'], 'yellow')))
            else:
                print()
            for item, dd in _d["symbols"][0].iteritems():



    def __store_api_info(self, query):
        url = "http://fanyi.youdao.com/openapi.do"
        payload = {
            "keyfrom": YOUDAO_KEYFROM,
            "key":YOUDAO_API_KEY,
            "type": "data",
            "doctype": "json",
            "version": "1.1",
            "q": query
        }

        self.__api_info["youdao"] = {"url": url, "payload": payload}

        url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
        q_from, q_to = ("zh", "en") if self.__is_chinese(query) else ("en", "zh")
        salt = random.randint(32768, 65536)
        m = hashlib.md5()
        weave = [BAIDU_APP_ID, query, str(salt), BAIDU_SECRET_KEY]
        m.update("".join(weave).encode("utf-8"))
        sign = m.hexdigest()
        payload = {
            "appid": BAIDU_APP_ID,  # APP ID
            "q": query,
            "from": q_from,  # 翻译源语言
            "to": q_to,  #
            "salt": salt,
            "sign": sign
        }

        self.__api_info["baidu"] = {"url": url, "payload": payload}

        url = "http://dict-co.iciba.com/api/dictionary.php"
        payload = {
            "w": query,        # 单词/汉字
            "type": "json",    # 返回格式 为空是xml 传入 xml 或者 json
            "key": ICIBA_KEY,  # 您申请到的key
        }

        self.__api_info["iciba"] = {"url": url, "payload": payload}

    def online_resources(query):
        common = [
            "http://www.iciba.com/{0}",
            "http://dict.youdao.com/w/{0}/#keyfrom=dict.index",
            "http://dict.cn/{0}"
        ]

        english = re.compile('^[a-z]+$', re.IGNORECASE)
        chinese = re.compile('^[\u4e00-\u9fff]+$', re.UNICODE)

        # Professional dictionary
        prof = [
            (english, 'http://www.ldoceonline.com/search/?q={0}'),
            (english, 'http://dictionary.reference.com/browse/{0}'),
            (english, 'http://www.urbandictionary.com/define.php?term={0}'),
            (chinese, 'http://www.zdic.net/sousuo/?q={0}')
        ]

        common = [url.format((query.encode('utf-8'))) for url in common]
        perf = [url.format((query.encode('utf-8'))) for lang, url in prof \
            if lang.match(query) is not None]

        return common + perf

    def __is_chinese(self, s):
        """判断是否为中文.
        如果字符串中含有一个汉子，则认为该字符串为中文"""
        for uchar in s:
            if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
                return True

        return False

class Daysay(object):
    def __init__(self):
        self.ds_data = {}
        self.debug = False

        self.__get_ds_data()

    def set_debuglevel(self, level):
        self.debug = level

    def __get_ds_data(self):
        url = DSAPI
        try:
            r = requests.get(url, timeout=10)
            if self.debug: print("Request url: ", r.url)
        except requests.exceptions.Timeout:
            print("Connection timeout!")
        except requests.exceptions.ConnectionError:
            print("Connection error!")
        except requests.exceptions.HTTPError:
            print("Invalid HTTP response!")

        if r.status_code == requests.codes.ok:
            try:
                self.ds_data = r.json()
                if self.debug: pprint(self.ds_data)
            except Exception as e:
                print("Error: ", e)
        else:
            print("Request was aborted, status code is", r.status_code)

    def print_daysay(self):
        ds_content = self.ds_data.get("content")
        ds_note = self.ds_data.get("note")

        if ds_content and ds_note:
            str_out = "\n" + ds_content + "\n" + ds_note + "\n"
            print(str_out)

    def feh_img(self):
        pass


# Script starts from here

if __name__ == "__main__":
    parser = ArgumentParser(description="Online dictionary based on the console.")
    parser.add_argument('-b', '--baidu',
                        action="store_true",
                        default=False,
                        help="Select baidu api.")
    parser.add_argument('-i', '--iciba',
                        action="store_true",
                        default=False,
                        help="Select iciba api.")
    parser.add_argument('-d', '--daysay',
                        action="store_true",
                        default=False,
                        help="Print daily sentence of iciba.")
    parser.add_argument('-f', '--refer',
                        action="store_true",
                        default=False,
                        help="Print online web resources.")
    parser.add_argument('-s', '--speech',
                        action="store_true",
                        default=False,
                        help="Print URL to speech audio.")
    parser.add_argument('-r', '--read',
                        action="store_true",
                        default=False,
                        help="Read out the word, use festival on Linux.")
    parser.add_argument('-x', '--selection',  # 划词
                        action="store_true",
                        default=False,
                        help="Show explaination of current selection.")
    parser.add_argument('words',
                        nargs='*',
                        help="Words to lookup, or quoted sentences to translate.")

    options = parser.parse_args()

    if options.baidu:
        select_api = SELECT_BAIDU
    elif options.iciba:
        select_api = SELECT_ICIBA
    else:
        select_api = SELECT_YOUDAO

    dictor = Dictor(select_api)
    dictor.set_debuglevel(DEBUG)

    if options.daysay:
        ds = Daysay()
        ds.set_debuglevel(DEBUG)
        ds.print_daysay()
    elif options.words:
        for word in options.words:
            word = word if PY3 else word.decode("utf-8")
            dictor.set_trans_data(word)
            dictor.print_trans_result()
