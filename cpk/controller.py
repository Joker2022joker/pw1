#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from cement.core import foundation, handler
from cement.core.controller import CementBaseController, expose, IController
from datetime import datetime

class CPKController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'CPK entry point'

    @expose()
    def default(self):
        self.app._meta.argv = ['-h']
        self._dispatch()

class NewController(CementBaseController):
    @expose
    def default(self):
        pass
