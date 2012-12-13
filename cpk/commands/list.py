#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from . import Command as IFace
from cpk.model import Attribute, session, Node
from cpk import exc

class Command(IFace):
    def children(self):
        if not self.args.nodes:
            return Node.root().lower()
        try:
            return Node.get(self.tokens_2_filters(self.tokenize_nodes())).lower()
        except exc.MatchedMultiple as e:
            import sys
            print("Couldnt match exactly, listing node: %s %s" % (e.last.attr.name, e.last.value), file=sys.stderr)
            return e.matched

    def _run(self,args):
        if self.args.attribute:
             return [ print(i.name) for i in session.query(Attribute).all()]

        rs = [ (i.attr.name, i.value) for i in self.children() ]

        if not rs:
            return

        rs.insert(0, ("Type","Value"))
        rs.insert(1, ("",""))

        just = max(map(lambda x: len(x),zip(*rs)))
        [ print("%s %s" % (x.rjust(just," "), y)) for x,y in rs]
