# -*- coding: utf-8 -*-

# Copyright (c) Huoty, All rights reserved
# Author: Huoty <sudohuoty@163.com>
# CreateTime: 2023-07-23 10:14:32

from __future__ import print_function

import os
import sys
import gc
import cmd
import time
from functools import partial
from subprocess import check_output
try:
    from distutils.spawn import find_executable
except ImportError:
    find_executable = lambda name: name

from .config import load_config
from .util import setdefaultencoding
from .dict import YoudaoDict, BaiduDict, IcibaDict


class DictShell(cmd.Cmd, object):

    def __init__(self, prompt=None, dict_api="youdao"):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = "tab"

        self.prompt = prompt or "Kictor> "

        self._dicts = {
            "youdao": YoudaoDict(),
            "baidu": BaiduDict(),
            "iciba": IcibaDict(),
        }
        self._selected_dict_api = dict_api

    def cmdloop(self):
        print("Kictor version 1.01, use Pyhton %s.%s.%s" % sys.version_info[:3])
        print("Input '@help' to view help message", end="\n\n")

        while True:
            try:
                super(DictShell, self).cmdloop()
                break
            except KeyboardInterrupt:
                print("^C")

    def postloop(self):
        print("\nBye")

    _api_cmd_mapping = {
        "youdao": "youdao",
        "y": "youdao",
        "iciba": "iciba",
        "i": "iciba",
        "baidu": "baidu",
        "b": "baidu",
    }

    def onecmd(self, text):
        text = text.strip()
        if text in ("@exit", "@quit", "@q"):
            return True
        if not text:
            return False

        if text.startswith("!"):
            os.system(text[1:])
        elif text.startswith("@"):
            _text = text[1:].strip()
            if _text in ("help", "?"):
                self.do_help()
            elif _text in self._api_cmd_mapping:
                self._selected_dict_api = self._api_cmd_mapping[_text]
            else:
                args = _text.split(' ', 1)
                is_multi_args = len(args) > 1
                if is_multi_args and args[0] in self._api_cmd_mapping:
                    dict_api = self._api_cmd_mapping[args[0]]
                    self.do_query(args[1].strip(), dict_api)
                elif is_multi_args and args[0] in {'r', 'read'}:
                    self.do_query(args[1].strip(), read=True)
                else:
                    self.do_query(text)
        else:
            self.do_query(text)
        return False

    def postcmd(self, stop, line):
        gc.collect()
        return stop

    def completenames(self, text, *ignored):
        pass

    def do_help(self):
        print()
        print("Commands help message:")
        print("=========================================================")
        print("@help, @?            Show this help message and continue")
        print("@youdao, @y          Switch to the youdao API")
        print("@iciba, @i           Switch to the iciba API")
        print("@baidu, @b           Switch to the baidu API")
        print("@read, @r            Read out the word")
        print("@exit, @quit, @q     Exit command mode")
        print("!<system command>    Run the system command")
        print()

    def do_query(self, word, selected_api=None, read=False):
        word = word.decode("utf-8") if sys.version_info[0] < 3 else word
        if selected_api:
            selected_api = self._api_cmd_mapping[selected_api]
        else:
            selected_api = self._selected_dict_api
        wdict = self._dicts[selected_api]
        wdict.query_and_show(word, read=read)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Kictor, a dictionary based on the console.")
    parser.add_argument('words',
                        nargs='*',
                        help="Words to lookup, or quoted sentences to translate.")
    parser.add_argument('-a', '--dict-api',  # 指定使用哪个词典 API
                        choices=['youdao', 'baidu', 'iciba'],
                        default='youdao',
                        help="Specify which dict API to use, default youdao.")
    parser.add_argument('-r', '--read',  # 阅读单词
                        action="store_true",
                        default=False,
                        help="Read out the word, use festival on Linux.")
    parser.add_argument('-x', '--selection',  # 划词
                        action="store_true",
                        default=False,
                        help="Show explaination of current selection.")
    parser.add_argument('-t', '--text',  # 去掉Ascii 颜色字符
                        action="store_true",
                        default=False,
                        help="Show plain text, without ascii color chars.")
    parser.add_argument('--debug',
                        action="store_true",
                        default=False,
                        help="Debug mode.")

    options = parser.parse_args()

    setdefaultencoding()

    if options.text:
        _c = lambda s, color='none': s

    load_config()

    dshell = DictShell(dict_api=options.dict_api)
    lookup_word = partial(dshell.do_query, read=options.read)

    if options.words:
        for word in options.words:
            lookup_word(word)
    else:
        if options.selection:
            xclip = find_executable("xclip")
            last = check_output([xclip, '-o'], universal_newlines=True)
            print("Waiting for selection>")
            while True:
                try:
                    time.sleep(0.1)
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
