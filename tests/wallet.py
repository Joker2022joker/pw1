#! /usr/bin/env python
# -*- coding: utf-8 -*-

from cpk.wallet import WalletProtocol, Service, Wallet
from nose.tools import eq_, raises, ok_
from unittest import TestCase
from cpk.crypto import Dummy

class CallCheck(object):
    def __init__(self):
        self.cnt = 0
    def __call__(self, *args, **kw):
        self.cnt += 1

def test_wallet_protocol_line_parser():
    p = WalletProtocol(None, None)

    data = b"foo\nbar\n\nbaz\n\n"
    expected = [b"foo\nbar", b"baz"]

    class LineReceived(object):
        def __init__(self):
            self.cnt = 0
        def __call__(self, line):
            eq_(expected[self.cnt],line)
            self.cnt += 1

    p.lineReceived = LineReceived()
    p.dataReceived(data)
    p.connectionLost()

    eq_(p.lineReceived.cnt, 2)

def test_wallet_protocol_lineReceived():
    p = WalletProtocol(None, Dummy())

    hc = CallCheck()
    rc = CallCheck()

    p.headerReceived = hc
    p.recordReceived = rc

    p.lineReceived(b'{}')
    eq_(hc.cnt, 1)
    eq_(rc.cnt, 0)

    p.lineReceived(b'{}')
    eq_(hc.cnt, 1)
    eq_(rc.cnt, 1)

def test_wallet_protocol_headerReceived():
    p = WalletProtocol(None, None)
    p.serviceReceived = CallCheck()
    p.headerReceived({'services': [1, 2]})

    eq_(p.serviceReceived.cnt, 2)

def test_wallet_protocol_serviceReceived():
    class DummyWallet:
        add_service = CallCheck()

    w = DummyWallet()
    eq_(w.add_service.cnt, 0)

    p = WalletProtocol(w, None)
    p.serviceReceived({'name': 'www',
            'id_as': ['host', 'user'],
            'password_as': ['pwd']})

    eq_(w.add_service.cnt, 1)

@raises(RuntimeError)
def test_wallet_protocol_nonempty_buffer_on_connectionLost():
    p = WalletProtocol(None, None)
    p.dataReceived(b"foo\n")
    p.connectionLost()

# {{{ serialization

class TestService(TestCase):
    def setUp(self):
        self.dict = {
            'name':'www',
            'id_as': ['host', 'user'],
            'password_as': ['pwd']}
        self.service = Service('www', ['host', 'user'],['pwd'])

    def test_to(self): 
        eq_(self.service.to_dict(), self.dict)

    def test_from(self):
        s = Service.from_dict(self.dict)
        eq_(s.__dict__, self.dict)

# }}}


def test_wallet_add_service():
    w = Wallet(Dummy)
    s = Service('www', ['host', 'user'],['pwd'])
    eq_(len(w.services.items()), 0)
    w.add_service(s)
    eq_(len(w.services.items()), 1)
    ok_(s.name in w.services)
    eq_(s, w.services[s.name])

@raises(RuntimeError)
def test_wallet_doesnt_accept_duplicit_services():
    w = Wallet(Dummy)
    s = Service('www', ['host', 'user'],['pwd'])
    w.add_service(s)
    w.add_service(s)
