#! /usr/bin/env python
# -*- coding: utf-8 -*-

from xdg.BaseDirectory import load_first_config
from cement.core import foundation, handler, hook, controller
import .controller as ctrl

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

    [handler.register(c) for c in dir(ctrl)
        if isinstance(c, controller.CementBaseController)]

    app.setup()
    app.run()
