#! /usr/bin/env python
# -*- coding: utf-8 -*-

from cpk.wallet import WalletProtocol, Service, Wallet, Record
from nose.tools import eq_, raises, ok_
from unittest import TestCase
from cpk.crypto import Dummy

class CallCheck(object):
    def __init__(self):
        self.cnt = 0
    def __call__(self, *args, **kw):
        self.cnt += 1

# {{{ Service
def test_service_contains():
    s = Service('www', ['host', 'user'],['pwd'])
    ok_('host' in s)
    ok_('pwd' in s)
    ok_('foo' not in s)

@raises(ValueError)
def test_service_attribute_uniqueness():
    Service('www', ['host'], ['host'])

class TestServiceOperators(TestCase):
    def setUp(self):
        self.x = Service('w', ['a'], ['b'])
        self.y = Service('w', ['a'], ['b'])

    def test_equals(self):
        eq_(self.x, self.y)

    def test_identity(self):
        ok_(not self.x is self.y)
# }}}

# {{{ Record
def test_record_type_check():
    Record(Service('www'))

@raises(TypeError)
def test_record_type_check2():
    Record('foo')

def test_record_add_attribute():
    s = Service('www', ['host', 'user'],['pwd'])
    r = Record(s)
    r.add_attribute('host', 'bar')
    eq_(r.attrs['host'], 'bar')

@raises(ValueError)
def test_record_attribute_check():
    s = Service('www', ['host', 'user'],['pwd'])
    r = Record(s)
    r.add_attribute('foo', 'bar')
# }}}

# {{{ WalletProtocol 
def test_wallet_protocol_line_parser():
    class DummyWallet(object):
        loaded = CallCheck()

    p = WalletProtocol(DummyWallet(), None)
    eq_(p.wallet.loaded.cnt, 0)

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

    eq_(p.wallet.loaded.cnt, 1)
    eq_(p.lineReceived.cnt, 2)

def test_wallet_protocol_lineReceived():
    class DummyWallet():
        def get_service(self, _):
            return Service('dummy')
    p = WalletProtocol(DummyWallet(), Dummy())

    hc = CallCheck()
    rc = CallCheck()

    p.headerReceived = hc
    p.recordReceived = rc

    p.lineReceived(b'{}')
    eq_(hc.cnt, 1)
    eq_(rc.cnt, 0)

    p.lineReceived(b'{"service": "a", "attrs":{}}')
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

# }}}

# {{{ serialization
class SerializationTester(object):
    # NOTE: these to/from methods are probably redundant with full_circle test
    def test_to(self):
        eq_(self.obj.to_dict(), self.dict)

    def test_from(self):
        s = self.cls.from_dict(self.dict, self.wallet)
        eq_(s, self.obj)

    def test_full_circle(self):
        s = self.cls.from_dict(self.obj.to_dict(), self.wallet)
        eq_(s, self.obj)

class TestService(TestCase, SerializationTester):
    def setUp(self):
        self.dict = {
            'name':'www',
            'id_as': ['host', 'user'],
            'password_as': ['pwd']}
        self.cls = Service
        self.obj = Service('www', ['host', 'user'],['pwd'])
        self.wallet = Wallet(Dummy())

class TestRecord(TestCase, SerializationTester):
    def setUp(self):
        self.dict = {
            'service': 'www',
            'attrs': {'host':'x', 'pwd': 'y'}}
        self.cls = Record
        self.service = Service('www', ['host'], ['pwd'])
        self.obj = Record(self.service,
            host='x', pwd='y')
        self.wallet = Wallet(Dummy())
        self.wallet.add_service(self.service)
# }}}

# {{{ Wallet
def test_wallet_add_service():
    w = Wallet(Dummy)
    w.serviceAdded = CallCheck()

    s = Service('www', ['host', 'user'],['pwd'])
    eq_(len(w.services.items()), 0)
    w.add_service(s)
    eq_(len(w.services.items()), 1)
    ok_(s.name in w.services)
    eq_(s, w.services[s.name])
    eq_(w.serviceAdded.cnt, 1)

def test_loaded_wallet_add_service():
    w = Wallet(Dummy)
    w.loaded()
    s = Service('www', ['host', 'user'],['pwd'])
    w.add_service(s)
    eq_(w._header_changed, True)

@raises(RuntimeError)
def test_wallet_doesnt_accept_duplicit_services():
    w = Wallet(Dummy)
    s = Service('www', ['host', 'user'],['pwd'])
    w.add_service(s)
    w.add_service(s)

def test_wallet_add_record():
    w = Wallet(Dummy())
    s = Service('www')
    r = Record(s)
    eq_(len(w.records), 0)
    w.add_record(r)
    eq_(len(w.records), 1)

class TestWalletClose(TestCase):
    def setUp(self):
        self.wallet = Wallet(Dummy())
        self.wallet._close = CallCheck()

    def test_no_change(self):
        self.wallet.close()
        eq_(self.wallet._close.cnt, 0)

    def test_service_change(self):
        self.wallet._header_changed = True
        self.wallet.close()
        eq_(self.wallet._close.cnt, 1)

    def test_record_change(self):
        self.wallet._record_changed = True
        self.wallet.close()
        eq_(self.wallet._close.cnt, 1)
# }}}
