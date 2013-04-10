#! /usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, abspath, join

from nose.tools import eq_, ok_, raises

from cpk.wallet import Wallet
from cpk.crypto import Dummy

def test_wallet_open():
    wfile = join(dirname(abspath(__file__)), "wallet.txt")
    w = Wallet.open(wfile, Dummy())
    eq_(len(w.records), 1)
    eq_(len(w.services.keys), 1)
