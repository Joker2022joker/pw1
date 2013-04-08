#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from cement.core import foundation, handler
from cement.core.controller import CementBaseController, expose, IController
from datetime import datetime
from .utils import tokenize_assignments

class CPKController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'CPK entry point'

    @expose()
    def default(self):
        self.app._meta.argv = ['-h']
        self._dispatch()

class NewController(CementBaseController):
    class Meta:
        interface = IController
        label = "new"
        description = "create new Record or Service"
        arguments = [
            (['-s', '--service'], dict(type=str, help='service')),
            (['args'], dict(metavar='spec', type=str, nargs='+', help='TODO')),
        ]
        # cpk new -s name pwd=x,y id=a,b
        # cpk new service=x host=y

        aliases = ['n']

    @expose()
    def default(self):
        print(self.pargs)
        print(tokenize_assignments(self.pargs.args))
