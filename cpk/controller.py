#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from cement.core import foundation, handler
from cement.core.controller import CementBaseController, expose
from datetime import datetime

class CPKController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'CPK entry point'

class NewController(CementBaseController):
    @expose
    def default(self):
        pass
