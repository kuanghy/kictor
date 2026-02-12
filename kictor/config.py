# -*- coding: utf-8 -*-

# Copyright (c) Huoty, All rights reserved
# Author: Huoty <sudohuoty@163.com>
# CreateTime: 2023-07-23 10:18:52

import os
import sys
from configparser import ConfigParser


config = ConfigParser()


# 系统用户目录
if sys.platform in ('win32', 'cygwin'):
    USER_HOME = os.getenv("USERPROFILE")
    if not USER_HOME:
        USER_HOME = os.getenv("HOME", "C:\\Users\\Administrator")
else:
    USER_HOME = os.getenv("HOME", "/root")


# 获取所有可能得配置文件路径
def _get_default_config_paths():
    config_dirs = [
        '/etc',
        '/usr/local/etc',
        os.path.join(USER_HOME, '.config'),
        os.path.join(USER_HOME, '.local', 'etc'),
        os.path.join(USER_HOME, '.kictor'),
    ]
    suffixes = [".ini", ".conf"]
    config_paths = [
        os.path.join(_dir, "kictor" + suffix)
        for _dir in config_dirs for suffix in suffixes
    ]
    config_paths.extend([
        os.path.join(_dir, "config.ini")
        for _dir in [os.path.join(USER_HOME, '.kictor'), os.getcwd()]
    ])
    return config_paths


# 被加载的配置文件
_LOADED_CONFIG_PATHS = []

# 标记配置是否已被加载过
_HAS_BEEN_LOADED = False


def load_config(path=None, reset=False):
    global _HAS_BEEN_LOADED, _LOADED_CONFIG_PATHS
    reset = bool(reset or path)
    if _HAS_BEEN_LOADED and not reset:
        return config

    for section in config.sections():
        config.remove_section(section)

    config_paths = _get_default_config_paths()
    if path and os.path.isfile(path):
        config_paths.append(path)

    _LOADED_CONFIG_PATHS = config.read(config_paths)
    _HAS_BEEN_LOADED = True
    return config
