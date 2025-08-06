# Copyright (c) Huoty, All rights reserved
# Author: Huoty <sudohuoty@163.com>

__version__ = "2.0.3"

from collections import namedtuple
_VersionInfo = namedtuple("version_info", ["major", "minor", "micro"])
version_info = ([int(v) for v in __version__.split('.')[:3]] + [0] * 3)[:3]
version_info = _VersionInfo(*version_info)
