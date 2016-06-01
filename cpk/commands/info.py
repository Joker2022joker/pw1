#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from cpk.model import session, Node, Attribute, Edge

class Command(IFace):
    def _run(self,args):
        print("db:\t{0}".format(self.app._get_db()))

        print("config:")
        for s in self.conf.sections():
            print("\t%s" % s)

            for i in self.conf.items(s):
                print("\t\t%s = %s" % i)

        countable = [Node, Attribute, Edge]
        for i in countable:
            cnt = session.query(i).count()
            print("%s count: %d" % (i.__name__, cnt))
