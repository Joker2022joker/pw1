#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace

class Command(IFace):
    def _run(self,args):
        print "db:\t{0}".format(self.app._get_db())
