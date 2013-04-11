#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import dirname, abspath
from collections import namedtuple

from nose.tools import eq_, ok_, raises

os.environ['XDG_DATA_HOME'] = dirname(abspath(__file__))
# NOTE: this seems to NEED to be set up before the xdg module is loaded

from cpk.wallet import Wallet, Service, Record
from cpk.crypto import Dummy
from cpk.controller import RecordController

FakePargs = namedtuple('FakePargs', ['service', 'args'])

def test_wallet_open():
    wfile = "wallet_deserialization.txt"
    w = Wallet.open(wfile, Dummy())
    eq_(len(w.records), 1)
    eq_(len(w.services.keys()), 1)

    s = Service('www', ['host', 'user'], ['pass'])
    eq_(w.services['www'], s)

    r = Record(s, host='example.com', user='laika', **{'pass':'nbusr123'})
    eq_(w.records[0], r)

def test_new_record_ctrl():
    class FakeApp(object):
        def __init__(self, wallet):
            self.wallet = wallet

    wallet = Wallet.open("wallet_new_record_ctrl.txt", Dummy())
    s = Service('www', ['host', 'user'], ['pass'])
    wallet.add_service(s)

    ctrl = RecordController()
    ctrl.app = FakeApp(wallet)
    ctrl.pargs = FakePargs('www', ['host=example.com', 'user=laika', 'pass=abcd'])

    ctrl.new()

    eq_(len(wallet.records), 1)
