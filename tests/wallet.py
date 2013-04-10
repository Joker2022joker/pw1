#! /usr/bin/env python
# -*- coding: utf-8 -*-

from cpk.wallet import WalletProtocol, Service, Wallet
from nose.tools import eq_, raises, ok_
from unittest import TestCase
from cpk.crypto import Dummy

def test_wallet_protocol():
    p = WalletProtocol(None)

    data = b"foo\nbar\n\nbaz\n\n"

    global iters
    iters = 0
    expected = [b"foo\nbar", b"baz"]

    def lineReceived(line):
        global iters
        # FIXME: why does the closure doesn't work (without the global)?
        eq_(expected[iters],line)
        iters += 1

    p.lineReceived = lineReceived
    p.dataReceived(data)
    p.connectionLost()

    eq_(iters, 2)


@raises(RuntimeError)
def test_wallet_protocol_nonempty_buffer_on_connectionLost():
    p = WalletProtocol(None)
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
