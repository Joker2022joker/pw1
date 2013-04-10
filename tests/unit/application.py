#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from cpk.app import Application, _setup_wallet, _setup_crypto_adapter
from cpk.wallet import Wallet
from cpk import crypto

from nose.tools import eq_, ok_

def test_wallet_hook():
    app = Application()
    app._setup_config_handler()
    app.crypto_adapter = crypto.Dummy()
    _setup_wallet(app)

    eq_(app.wallet.__class__, Wallet)

def test_crypto_hook():
    app = Application()
    app._setup_config_handler()
    _setup_crypto_adapter(app)
    ok_(isinstance(app.crypto_adapter,crypto.Interface))
