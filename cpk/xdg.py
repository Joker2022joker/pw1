#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from os.path import join

from xdg.BaseDirectory import load_first_config as lfc
from xdg.BaseDirectory import save_data_path as sdp

__xdg_namespace__ = 'cpk'

def load_first_config(*xs, **kw):
    return lfc(__xdg_namespace__, *xs, **kw)

def save_data_path(*xs, **kw):
    return sdp(__xdg_namespace__, *xs, **kw)

def save_data_file(f):
    return join(save_data_path(), f)
