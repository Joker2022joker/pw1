#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xdg.BaseDirectory import load_first_config
from cement.core import foundation, handler, hook, controller

from . import controller as ctrl
from .utils import ctrls

class Application(foundation.CementApp):
    class Meta:
        label = 'CPK'
        base_controller = ctrl.CPKController
        config_defaults = {
            'debug': {
                'encrypt':'on'},
            'main': {
                'db':'wallet-0.2.asc',
                'input_kill_0x0a': "on",
                'output_kill_0x0a': "on"}}

def main():
    app = Application()

    for c in ctrls([getattr(ctrl, x) for x in dir(ctrl)]):
        handler.register(c)

    app.setup()
    app.run()
