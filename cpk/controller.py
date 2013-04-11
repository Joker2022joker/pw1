#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import datetime

from cement.core import foundation, handler
from cement.core.controller import CementBaseController, expose, IController

from .utils import tokenize_assignments
from .wallet import Record, Service

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
        description = "Record"
        arguments = [
            (['-s', '--service'], dict(type=str, help='service')),
            (['attrs'], dict(metavar='attributes', type=str, nargs='+',
                help='name=value')),
        ]

        aliases = ['r']

    @expose()
    def new(self):
        try:
            s = self.app.wallet.get_service(self.pargs.service)
        except KeyError:
            raise #TODO

        r = Record(s, **tokenize_assignments(self.pargs.attrs))
        self.app.wallet.add_record(r)

class ServiceController(CementBaseController):
    class Meta:
        interface = IController
        label = "service"
        description = "Service"
        arguments = [
            (['-s', '--service'], dict(type=str, help='service name')),
            (['-p', '--passwords'], dict(type=str, help='password attribute'
                ' names', nargs='+', metavar='pwds')),
            (['-i', '--identificators'], dict(help='record identificator'
                ' attributes', type=str, nargs='*', metavar='ids')),
        ]

        aliases = ['s']

    @expose()
    def new(self):
        s = Service(self.pargs.service, self.pargs.ids, self.pargs.pwds)
        self.app.wallet.add_service(s)
