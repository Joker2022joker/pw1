#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import dirname, abspath
from collections import namedtuple

from nose.tools import eq_, ok_, raises
from unittest import TestCase

os.environ['XDG_DATA_HOME'] = dirname(abspath(__file__))
# NOTE: this seems to NEED to be set up before the xdg module is loaded

from cpk.wallet import Wallet, Service, Record
from cpk.crypto import Dummy
from cpk.controller import RecordController, ServiceController

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

    FakePargs = namedtuple('FakePargs', ['service', 'attrs'])

    wallet = Wallet.open("wallet_new_record_ctrl.txt", Dummy())
    s = Service('www', ['host', 'user'], ['pass'])
    wallet.add_service(s)

    ctrl = RecordController()
    ctrl.app = FakeApp(wallet)
    ctrl.pargs = FakePargs('www', ['host=example.com', 'user=laika', 'pass=abcd'])

    eq_(len(wallet.records), 0)
    ctrl.new()
    eq_(len(wallet.records), 1)

class NewServiceTester(object):
    def test_new_service_ctrl(self):
        class FakeApp(object):
            def __init__(self, wallet):
                self.wallet = wallet

        wallet = Wallet.open("wallet_new_service_ctrl.txt", Dummy())

        ctrl = ServiceController()
        ctrl.app = FakeApp(wallet)
        ctrl.pargs = self.pargs

        eq_(wallet._header, None)
        ctrl.new()

        eq_(len(wallet.services.values()), 1)
        eq_(self.service, wallet.services['www'])

class NewService(TestCase, NewServiceTester):
    def setUp(self):
        FakePargs = namedtuple('FakePargs', ['service', 'pwds', 'ids'])
        self.pargs = FakePargs('www', ['pass'], ['host', 'user'])
        self.service = Service(self.pargs.service, self.pargs.ids, self.pargs.pwds)

class NewServiceNoIdAttributes(TestCase, NewServiceTester):
    def setUp(self):
        FakePargs = namedtuple('FakePargs', ['service', 'pwds'])
        self.pargs = FakePargs('www', ['pass'])
        self.service = Service(self.pargs.service, [], self.pargs.pwds)

# TODO: test the argparser results maybe?
