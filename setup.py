#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import cpk

setup(
    name='cpk',
    version=cpk.__version__,
    description='Password Manager storing data in gnupg encrypted graph',
    author='Jan Matejka',
    author_email='yac@blesmrt.net',
    url='https://github.com/yaccz/cpk',

    packages = find_packages(
        where = '.'
    ),

    install_requires = [
        "setuptools",
        "argparse", # see cement issue 187
        "cement",
        "pyxdg",
    ],

    extras_require = {
        'python_gnupg': ["python-gnupg"],
    },

    package_data = {
        "cpk": [ "data/*/*" ]
    },

    entry_points = {
        'console_scripts': ['cpk = cpk.app:main']},
)
