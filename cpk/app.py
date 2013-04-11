#! /usr/bin/env python
# -*- coding: utf-8 -*-

from cement.core import foundation, handler, hook, controller

from . import controller as ctrl
from .utils import ctrls
from .wallet import Wallet
from . import crypto
from .xdg import load_first_config

try:
    from ConfigParser import NoSectionError
except ImportError:
    from configparser import NoSectionError

c = load_first_config("config-0.2.0.ini")
configs = [c] if c else []

class Application(foundation.CementApp):
    """
        :ivar crypto_adapter: `crypto.Interface`
        :ivar wallet: `Wallet`
    """
    class Meta:
        label = 'CPK'
        base_controller = ctrl.CPKController
        config_defaults = {
            'debug': {
                'encrypt':'on'},
            'main': {
                'db': 'wallet-0.2.asc',
                'adapter': 'Dummy',
                'input_kill_0x0a': "on",
                'output_kill_0x0a': "on"},}

        config_files = configs

def _setup_crypto_adapter(app):
    name = app.config.get('main', 'adapter')
    adapter = getattr(crypto, name)

    try:
        cg = app.config.items('crypto.{0}'.format(name))
    except NoSectionError:
        # NOTE: this is not compatible with using different Config Handler in
        # cement but oh well, I don't care atm.
        cg = []

    app.crypto_adapter = adapter(cg)

def _setup_wallet(app):
    app.wallet = Wallet.open(app.config.get('main','db'), app.crypto_adapter)

def _close_wallet(app):
    app.wallet.close()

def main():
    app = Application()

    for c in ctrls([getattr(ctrl, x) for x in dir(ctrl)]):
        handler.register(c)
    hook.register('post_setup', _setup_crypto_adapter, weight=0)
    hook.register('post_setup', _setup_wallet, weight=10)
    hook.register('pre_close', _close_wallet)

    try:
        app.setup()
        app.run()
    finally:
        app.close()
