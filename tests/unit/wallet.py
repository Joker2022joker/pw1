#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from nose.tools import eq_, raises, ok_
from unittest import TestCase

from cpk.crypto import Dummy
from cpk.wallet import WalletProtocol, Service, Wallet, Record, Header
from cpk.wallet import LineRecord

log = logging.getLogger(__name__)

class CallCheck(object):
    def __init__(self):
        self.cnt = 0
    def __call__(self, *args, **kw):
        self.cnt += 1

# {{{ LineRecord
def test_LineRecord_changed():
    o = LineRecord()
    o.raw = 'foo'
    o.changed()
    eq_(o.raw, None)
# }}}

# {{{ Header
@raises(RuntimeError)
def test_header_doesnt_accept_duplicit_services():
    w = Wallet(Dummy)
    h = Header(w)
    s = Service('www', ['host', 'user'],['pwd'])
    h.add_service(s)
    h.add_service(s)

# }}}

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

@raises(RuntimeError)
def test_unclean_conn_close():
    p = WalletProtocol(Wallet(None), None)
    p.connectionLost(False)

def test_wallet_protocol__sendLineRecord():
    class TestProtocol(WalletProtocol):
        def sendLine(self, line):
            self._sent_line = line

    p = TestProtocol(Wallet(Dummy()), Dummy())
    ok_(not hasattr(p, '_sent_line'))
    p._sendLineRecord(Service('www', ['a'], ['b']))
    eq_(p._sent_line, '{"password_as": ["b"], "id_as": ["a"], "name": "www"}')
    # FIXME: check calls, not output

@raises(RuntimeError)
def test_wallet_protocol_sendLineRecord():
    p = WalletProtocol(Wallet(Dummy()), Dummy())
    p.sendLine = CallCheck()
    h = Header(p.wallet)
    h.add_service(Service('www', ['a'], ['b']))
    p.sendLineRecord(h)
    p.sendLineRecord(h)

def test_wallet_protocol_sendLineRecord_sends_raw():
    p = WalletProtocol(Wallet(Dummy()), Dummy())
    p.sendLine = CallCheck()
    p._sendLineRecord = CallCheck()
    h = Header(p.wallet)
    h.raw = 'foo'
    h.add_service(Service('www', ['a'], ['b']))
    p.sendLineRecord(h)
    eq_(p.sendLine.cnt, 1)
    eq_(p._sendLineRecord.cnt, 0)

class TestWalletProtocolLineReceived(TestCase):
    def setUp(self):
        class DummyWallet():
            _header = None
            def get_service(self, _):
                return Service('dummy')
        self.p = WalletProtocol(DummyWallet(), Dummy())

        self.hc = CallCheck()
        self.rc = CallCheck()

        self.p._headerDictReceived = self.hc
        self.p.recordReceived = self.rc

        eq_(self.hc.cnt, 0)
        eq_(self.rc.cnt, 0)

    def test_header(self):
        self.p.lineReceived(b'{"services":[]}')
        eq_(self.hc.cnt, 1)
        eq_(self.rc.cnt, 0)

    def test_record(self):
        Header(self.p.wallet)
        self.p.lineReceived(b'{"service": "a", "attrs":{}}')
        eq_(self.hc.cnt, 0)
        eq_(self.rc.cnt, 1)

def test_wallet_protocol_recordReceived():
    class DummyWallet():
        add_record = CallCheck()
    p = WalletProtocol(DummyWallet(), None)

    eq_(p.wallet.add_record.cnt, 0)
    p.recordReceived(None)
    eq_(p.wallet.add_record.cnt, 1)

def test_wallet_protocol_headerLineReceived():
    p = WalletProtocol(Wallet(None), None)
    ok_(not p.wallet._header)
    p._headerDictReceived({"services":[]})
    ok_(p.wallet._header)

def test_header_from_dict():
    w = Wallet(None)
    d = {'services':[{'name': 'www',
            'id_as': ['host', 'user'],
            'password_as': ['pwd']}]}

    h = Header.from_dict(d, w)
    ok_('www' in w.services)

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
        Header(self.wallet)
        self.wallet.add_service(self.service)

class TestHeader(TestCase, SerializationTester):
    def setUp(self):
        self.cls = Header
        self.dict = {
            'services': [{'name': 'www', 'id_as': ['a'], 'password_as': ['b']}]}
        self.wallet = Wallet(Dummy())
        self.obj = Header(self.wallet)
        self.obj.add_service(Service('www', ['a'], ['b']))

        log.debug(self.obj.to_dict())
# }}}

# {{{ Wallet
def test_wallet_add_service():
    w = Wallet(Dummy)
    h = Header(w)

    s = Service('www', ['host', 'user'],['pwd'])
    eq_(len(w.services.items()), 0)
    w.add_service(s)
    eq_(len(w.services.items()), 1)
    ok_(s.name in w.services)
    eq_(s, w.services[s.name])

def test_loaded_wallet_add_service():
    w = Wallet(Dummy)
    h = Header(w)
    h.raw = 'foo'
    w.loaded()
    s = Service('www', ['host', 'user'],['pwd'])
    w.add_service(s)
    eq_(w._header.raw, None)

@raises(RuntimeError)
def test_wallet_doesnt_accept_duplicit_services():
    w = Wallet(Dummy)
    Header(w)
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
        Header(self.wallet)
        self.wallet._header.raw = 'kek'
        self.wallet._close = CallCheck()

    def test_no_change(self):
        self.wallet.close()
        eq_(self.wallet._close.cnt, 0)

    def test_service_change(self):
        self.wallet._header.changed()
        self.wallet.close()
        eq_(self.wallet._close.cnt, 1)

    def test_record_change(self):
        self.wallet.record_changed = lambda: True
        self.wallet.close()
        eq_(self.wallet._close.cnt, 1)

@raises(RuntimeError)
def test_wallet__open_notfile():
    w = Wallet(Dummy())
    w._open("/tmp")

def test_wallet__open():
    class DummyProtocol(WalletProtocol):
        def dataReceived(self, _):
            self.__class__.drc = True

        def connectionLost(self, _=None):
            self.__class__.clc = True

    w = Wallet(Dummy())
    w.protocol = DummyProtocol
    from tempfile import mkstemp
    _, wfile = mkstemp()
    with open(wfile, "wb") as f:
        f.write("foo")

    w._open(wfile)
    ok_(DummyProtocol.clc)
    ok_(DummyProtocol.drc)

def test_wallet_record_not_changed():
    w = Wallet(None)
    Header(w)
    s = Service('www', ['a'], ['b'])
    w.add_service(s)
    r1 = Record(s, a='a', b='b')
    r2 = Record(s, a='a1', b='b')
    r2.raw = r1.raw = 'foo'
    w.add_record(r1)
    w.add_record(r2)
    ok_(not w.record_changed())

def test_wallet_record_changed():
    w = Wallet(None)
    Header(w)
    s = Service('www', ['a'], ['b'])
    w.add_service(s)
    r1 = Record(s, a='a', b='b')
    r2 = Record(s, a='a1', b='b')
    r1.raw = 'foo'
    w.add_record(r1)
    w.add_record(r2)
    ok_(w.record_changed())
# }}}
