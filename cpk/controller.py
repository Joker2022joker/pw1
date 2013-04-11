#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import datetime

from cement.core import foundation, handler
from cement.core.controller import CementBaseController, expose, IController

from .utils import tokenize_assignments
from .wallet import Record

class CPKController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'CPK entry point'

    @expose()
    def default(self):
        self.app._meta.argv = ['-h']
        self._dispatch()

class RecordController(CementBaseController):
    class Meta:
        interface = IController
        label = "record"
        description = "Record stuff" # TODO
        arguments = [
            (['-s', '--service'], dict(type=str, help='service')),
            (['args'], dict(metavar='spec', type=str, nargs='+', help='TODO')),
        ]

        aliases = ['r']

    @expose()
    def new(self):
        try:
            s = self.app.wallet.get_service(self.pargs.service)
        except KeyError:
            raise #TODO

        r = Record(s, **tokenize_assignments(self.pargs.args))
        self.app.wallet.add_record(r)
