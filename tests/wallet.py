#! /usr/bin/env python
# -*- coding: utf-8 -*-

from cpk.wallet import WalletProtocol
from nose.tools import eq_, raises

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
