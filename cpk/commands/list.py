#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from . import Command as IFace
from model import Attribute, session, Node

class Command(IFace):
    def children(self):
        if not self.args.nodes:
            return Node.root().lower_neighbors()

        return Node.get(self.tokenize_nodes()).lower_neighbors()

    def _run(self,args):
        if self.args.attribute:
             return [ print(i.name) for i in session.query(Attribute).all()]
           
        rs = [ (i.attr().name, i.value) for i in self.children() ]

        if not rs:
            return

        rs.insert(0, ("Type","Value"))
        rs.insert(1, ("",""))

        just = max(map(lambda x: len(x),zip(*rs)))
        [ print("%s %s" % (x.rjust(just," "), y)) for x,y in rs]
