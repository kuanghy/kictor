# -*- coding: utf-8 -*-

__version__ = "2.0.0"


def load_ipython_extension(ipython):
    from .cli import ipython_magic_function
    ipython.register_magic_function(ipython_magic_function, 'line', 'kict')
    ipython.register_magic_function(ipython_magic_function, 'cell', 'kict')
