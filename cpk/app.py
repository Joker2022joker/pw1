#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xdg.BaseDirectory import load_first_config
from cement.core import foundation, handler, hook, controller

from . import controller as ctrl
from .utils import ctrls
from .wallet import Wallet
from . import crypto

class Application(foundation.CementApp):
    class Meta:
        label = 'CPK'
        base_controller = ctrl.CPKController
        config_defaults = {
            'debug': {
                'encrypt':'on'},
            'main': {
                'db': 'wallet-0.2.asc',
                'adapter': 'GnuPGInterface',
                'input_kill_0x0a': "on",
                'output_kill_0x0a': "on"},
            'crypto.GnuPGInterface':{
                }}

def _setup_wallet(app):
    adapter_name = app.config.get('main', 'adapter')
    adapter = getattr(crypto, adapter_name)
    adapter_config = app.config.items('crypto.{0}'.format(adapter_name))
    adapter = adapter(adapter_config)

    app.wallet = Wallet.open(app.config.get('main','db'), adapter)

def main():
    app = Application()

    for c in ctrls([getattr(ctrl, x) for x in dir(ctrl)]):
        handler.register(c)
    hook.register('post_setup', _setup_wallet)

    app.setup()
    app.run()
