#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from cpk.app import Application, _setup_wallet
from cpk.wallet import Wallet

from nose.tools import eq_

def test_wallet_hook():
    app = Application()
    app._setup_config_handler()
    _setup_wallet(app)

    eq_(app.wallet.__class__, Wallet)

