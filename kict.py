#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#     Filename @  kict.py
#       Author @  Huoty
#  Create date @  2016-04-10 09:18:02
#  Description @  The console of the dictionary
# *************************************************************

from __future__ import print_function

import os
import sys
import re
import gc
import cmd
import json
import random
import hashlib
import platform
from functools import partial
from subprocess import Popen, call
from distutils.spawn import find_executable

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    from urllib2 import Request, urlopen
except ImportError:
    from urllib.request import Request, urlopen


if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# youdao api
YOUDAO_KEYFROM = "Kictor"
YOUDAO_API_KEY = "2047746926"

# baidu api
BAIDU_APP_ID = "20160409000018177"
BAIDU_SECRET_KEY = "qwJBEKy7dcychROiwMMk"

# iciba api
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

    def __call__(self, s, color='none'):
        if color in self.colors:
            return "{0}{1}{2}".format(
                self.colors[color],
                s,
                self.colors['default'])
        else:
            return s


_c = Colorizing()


class CachedProperty(object):

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__)
        if value is None:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value

        return value


class Base(object):

    @staticmethod
    def _get_request(url, params=None, timeout=10):
        """HTTP GET Request"""
        if params:
            params = urlencode(params)
            url = "?".join([url, params])
        request = Request(url)
        resp = urlopen(request, timeout=timeout)
        body = resp.read().decode("utf-8")
        if resp.getcode() != 200:
            raise Exception(body)
        return body

    @staticmethod
    def _is_chinese(text):
        """判断是否为中文，如果字符串中含有一个汉子，则认为该字符串为中文"""
        for uchar in text:
            if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
                return True
        return False


class WebDict(Base):
    """在线网络词典"""

    def __init__(self, selected_api="youdao", debug=False):
        self.selected_api = selected_api
        self.debug = debug  # 是否开启 debug 模式
        self.query = ""     # 需要翻译的内容
        self.has_result = False  # 是否有翻译结果

    @property
    def api_info(self):
        api_info = {}  # 存放所有支持的词典接口信息

        # 有道词典开放接口
        url = "http://fanyi.youdao.com/openapi.do"
        payload = {
            "keyfrom": YOUDAO_KEYFROM,
            "key": YOUDAO_API_KEY,
            "type": "data",
            "doctype": "json",
            "version": "1.2",
            "q": self.query
        }

        api_info["youdao"] = {"url": url, "payload": payload}

        # 百度翻译开放接口
        url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
        q_from, q_to = ("zh", "en") if self._is_chinese(self.query) else ("en", "zh")
        salt = random.randint(32768, 65536)
        m = hashlib.md5()
        weave = [BAIDU_APP_ID, self.query, str(salt), BAIDU_SECRET_KEY]
        m.update("".join(weave).encode("utf-8"))
        sign = m.hexdigest()
        payload = {
            "appid": BAIDU_APP_ID,  # APP ID
            "q": self.query,
            "from": q_from,  # 翻译源语言
            "to": q_to,  #
            "salt": salt,
            "sign": sign
        }

        api_info["baidu"] = {"url": url, "payload": payload}

        # 金山词霸开放接口
        url = "http://dict-co.iciba.com/api/dictionary.php"
        payload = {
            "w": self.query.lower(),  # 单词/汉字
            "type": "json",           # 返回格式 为空是xml 传入 xml 或者 json
            "key": ICIBA_KEY,         # 您申请到的key
        }

        api_info["iciba"] = {"url": url, "payload": payload}

        return api_info

    @property
    def trans_data(self):
        url = self.api_info[self.selected_api]["url"]
        payload = self.api_info[self.selected_api]["payload"]
        try:
            resp_body = self._get_request(url, params=payload, timeout=10)
            return json.loads(resp_body)
        except Exception as e:
            print(e)

    def print_trans_result(self, speech=False, resource=False, read=False):
        if self.selected_api == "baidu":
            self._show_baidu_trans_result()
        elif self.selected_api == "iciba":
            self._show_iciba_trans_result(speech)
        else:
            self._show_youdao_trans_result(speech)

        if not self.has_result:
            print(_c(' -- No result for this query.', 'red'))
        elif resource:
            self.show_resources()
        elif read:
            self.read_word()

        print()

    def show_resources(self):
        """Online resources"""
        ol_res = self._online_resources
        if len(ol_res) > 0:
            print(_c('\n  在线资源:', 'cyan'))
            print(*map(('     * ' + _c('{0}', 'underline')).format, ol_res), sep='\n')
        else:
            print(_c('    -- No online resources for this query.', 'red'))

    def read_word(self):
        """Read out the word"""
        sys_name = platform.system()
        if 'Darwin' == sys_name:
            call(['say', self.query])
        elif 'Linux' == sys_name:
            if find_executable('festival'):
                Popen('echo ' + self.query + ' | festival --tts', shell=True)
            else:
                print(_c(' -- Please Install festival.', 'red'))
        else:
            print(_c(' -- Failed to read out the word.', 'red'))

    def _show_youdao_trans_result(self, speech=False):
        _d = self.trans_data
        if not _d:
            return

        print(_c(self.query, 'bold'), end='')

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

            if speech and 'speech' in _b:
                print(_c('  发音参考:', 'cyan'))
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
                ) for ref in _d['web']], sep='\n')

    def _show_baidu_trans_result(self):
        _d = self.trans_data
        if not _d:
            return

        if "trans_result" in _d:
            self.has_result = True
            trans_result = _d["trans_result"][0]
            print(_c(trans_result["src"], 'bold'))
            print(_c("  翻译结果:", 'cyan'))
            print(_c("     * {0}".format(trans_result["dst"]), 'magenta'))

    def _show_iciba_trans_result(self, speech=False):
        _d = self.trans_data
        if not _d:
            return

        print(_c(self.query, 'bold'), end='')

        symbols = _d["symbols"][0]
        if self._is_chinese(self.query) and "parts" in symbols:
            self.has_result = True

            if symbols.get("word_symbol"):
                print(" [{0}]".format(_c(symbols["word_symbol"], "yellow")))
            else:
                print()

            if speech:
                print(_c('  读音参考:', 'cyan'))
                if symbols.get("symbol_mp3"):
                    print("     * ", symbols["symbol_mp3"])
                else:
                    print(_c(' -- No speech for this query.', 'red'))
                print()

            parts = symbols["parts"][0]
            print(_c('  词典释义:', 'cyan'))
            means = [mean.get("word_mean") for mean in parts["means"] if mean.get("word_mean")]
            print(*map("    * {0}".format, means), sep='\n')
        elif "parts" in symbols:
            self.has_result = True

            if symbols.get("ph_en") and symbols.get("ph_am"):
                print(" UK: [{0}]".format(_c(symbols["ph_en"], 'yellow')), end=',')  # 英式发音
                print(" US: [{0}]".format(_c(symbols["ph_am"], 'yellow')))  # 美式发音
            elif symbols.get('ph_other'):
                print(" [{0}]".format(_c(symbols['ph_other'], 'yellow')))
            else:
                print()

            if speech:
                print(_c('  发音参考:', 'cyan'))
                speech_count = 0
                if symbols.get('ph_en_mp3'):
                    print("     * UK:", symbols["ph_en_mp3"])
                    speech_count += 1
                if symbols.get('ph_am_mp3'):
                    print("     * US:", symbols["ph_am_mp3"])
                    speech_count += 1
                if symbols.get('ph_tts_mp3'):
                    print("     * TTS:", symbols['ph_tts_mp3'])
                    speech_count += 1

                if speech_count == 0:
                    print(_c(' -- No speech for this query.', 'red'))

                print()

            parts = symbols["parts"]
            print(_c('  词典释义:', 'cyan'))
            print(*[
                '     * {0}\n       {1}'.format(
                    _c(part['part'], 'yellow'),
                    '; '.join(map('{0}'.format, part['means']))
                ) for part in symbols["parts"]], sep='\n')

            if "exchange" in _d:
                print(_c('\n  单词时态:', 'cyan'))
                exchange_count = 0
                exchange_items = _d["exchange"].iteritems if sys.version_info[0] < 3 else _d["exchange"].items
                for t, w in exchange_items():
                    if w:
                        print("     * {0}: {1}".format(_c(t.split('_')[1], "green"), ", ".join(w)))
                        exchange_count += 1
                if exchange_count == 0:
                    print(_c('    -- No tense for this query.', 'red'))
        else:
            print()

    @property
    def _online_resources(self):
        common = [
            "http://dict.cn/{0}",
            "http://www.iciba.com/{0}",
            "http://dict.youdao.com/w/{0}/#keyfrom=dict.index"
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

        common = [url.format((self.query.encode('utf-8'))) for url in common]
        perf = [url.format((self.query.encode('utf-8'))) for lang, url in prof
                if lang.match(self.query) is not None]

        return common + perf


class Daysay(Base):

    def __init__(self):
        pass

    def _fetch_ds_data(self):
        resp_body = self._get_request(DSAPI, timeout=3)
        return json.loads(resp_body)

    def show(self, show_translation=False):
        data = self._fetch_ds_data()
        content = data.get("content")
        note = data.get("note")
        if content and note:
            str_out = "\n{}\n{}\n".format(_c(content, "yellow"), _c(note, "magenta"))
            print(str_out)

        translation = data.get("translation")
        if show_translation is True and translation:
            print(translation, end='\n\n')


class DictShell(Base, cmd.Cmd):

    def __init__(self, prompt=None):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = "tab"

        self.prompt = prompt or "Kictor> "

        self.wdict = WebDict()
        self._selected_dict_api = "youdao"

    def cmdloop(self):
        print("Kictor version 1.01, use Pyhton %s.%s.%s" % sys.version_info[:3])
        print("Input '@help' to view help message")

        try:
            Daysay().show(show_translation=True)  # 显示爱词霸每日一句
        except Exception as e:
            print("Daysay show error: ", e)

        while True:
            try:
                super(DictShell, self).cmdloop()
                break
            except KeyboardInterrupt:
                print("^C")

    def postloop(self):
        print("\nBye")

    def onecmd(self, text):
        text = text.strip()
        if not text:
            return False

        if text in ("@help", "@?"):
            self.do_help()
            return False

        if text in ("@exit", "@quit", "@q", "EOF"):
            return True

        if text.startswith("!"):
            os.system(text[1:])
            return False

        if text.startswith("@select_"):
            self._selected_dict_api = text.split("_")[1]
            return False

        self.do_query(text)

    def postcmd(self, stop, line):
        gc.collect()
        return stop

    def completenames(self, text, *ignored):
        pass

    def do_help(self):
        print()
        print("Commands help message:")
        print("=========================================================")
        print("@help, @?             Show this help message and continue")
        print("@select_youdao_api    Switch to the youdao API")
        print("@select_iciba_api     Switch to the iciba API")
        print("@select_baidu_api     Switch to the baidu API")
        print("@exit, @quit, @q      Exit command mode")
        print("!<system command>     Run the system command")
        print()

    def do_query(self, word, selected_api=None, speech=False, resource=False, read=False):
        word = word.decode("utf-8") if sys.version_info[0] < 3 else word
        self.wdict.selected_api = selected_api or self._selected_dict_api
        self.wdict.query = word
        self.wdict.print_trans_result(speech, resource, read)


# Script starts from here

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Kictor, online dictionary based on the console.")
    parser.add_argument('words',
                        nargs='*',
                        help="Words to lookup, or quoted sentences to translate.")
    parser.add_argument('-b', '--baidu',  # 百度翻译
                        action="store_true",
                        default=False,
                        help="Select baidu api.")
    parser.add_argument('-i', '--iciba',  # 爱词霸
                        action="store_true",
                        default=False,
                        help="Select iciba api.")
    parser.add_argument('-d', '--daysay',  # 每日一句
                        action="store_true",
                        default=False,
                        help="Print daily sentence of iciba.")
    parser.add_argument('-o', '--resources',  # 在线资源
                        action="store_true",
                        default=False,
                        help="Print online web resources.")
    parser.add_argument('-s', '--speech',  # 发音文件
                        action="store_true",
                        default=False,
                        help="Print URL to speech audio.")
    parser.add_argument('-r', '--read',  # 阅读单词
                        action="store_true",
                        default=False,
                        help="Read out the word, use festival on Linux.")
    parser.add_argument('-x', '--selection',  # 划词
                        action="store_true",
                        default=False,
                        help="Show explaination of current selection.")
    parser.add_argument('--debug',
                        action="store_true",
                        default=False,
                        help="Debug mode")

    options = parser.parse_args()

    if options.daysay:
        try:
            Daysay().show(show_translation=True)
        except Exception as e:
            print(_c(e, "red"))
    else:
        dshell = DictShell()

        if options.baidu:
            dshell._selected_dict_api = "baidu"
        elif options.iciba:
            dshell._selected_dict_api = "iciba"
        else:
            dshell._selected_dict_api = "youdao"

        lookup_word = partial(dshell.do_query, speech=options.speech,
                              resource=options.resources, read=options.read)

        if options.words:
            for word in options.words:
                lookup_word(word)
        else:
            if options.selection:
                from subprocess import check_output
                from time import sleep
                xclip = find_executable("xclip")
                last = check_output([xclip, '-o'], universal_newlines=True)
                print("Waiting for selection>")
                while True:
                    try:
                        sleep(0.1)
                        curr = check_output([xclip, '-o'], universal_newlines=True)
                        if curr != last:
                            last = curr
                            if last.strip():
                                lookup_word(last)
                            print("Waiting for selection>")
                    except (KeyboardInterrupt, EOFError):
                        break
            else:
                dshell.cmdloop()
