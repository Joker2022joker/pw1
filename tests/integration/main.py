#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import dirname, abspath

from nose.tools import eq_, ok_, raises

os.environ['XDG_DATA_HOME'] = dirname(abspath(__file__))
# NOTE: this seems to NEED to be set up before the xdg module is loaded

from cpk.wallet import Wallet
from cpk.crypto import Dummy

def test_wallet_open():
    wfile = "wallet_deserialization.txt"
    w = Wallet.open(wfile, Dummy())
    eq_(len(w.records), 1)
    eq_(len(w.services.keys()), 1)
