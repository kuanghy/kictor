#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


CURRDIR = os.path.dirname(os.path.abspath(__file__))


setup_args = dict(
    name='kictor',
    version='0.0.1',
    description='A dictionary based on the console',
    packages=find_packages(exclude=("tests", "tests.*")),
    author='huoty',
    author_email='sudohuoty@163.com',
    url='https://github.com/kuanghy/kictor',
    zip_safe=False,
    platforms=["any"],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)


def get_version():
    version = '1.0'
    scope = {}
    version_file = os.path.join(CURRDIR, "kictor", "version.py")
    if os.path.exists(version_file):
        with open(version_file) as fp:
            exec(fp.read(), scope)
        version = scope.get('__version__', '1.0')
    return version


def main():
    setup_args["version"] = get_version()
    setup_args["entry_points"] = {
        'console_scripts': [
            'kict=kictor.cli:main',
        ],
    }
    setup(**setup_args)


if __name__ == "__main__":
    main()
