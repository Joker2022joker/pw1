#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from cpk.model import Attribute, session, Node
from cpk import exc

class Command(IFace):
    def _run(self,args):
        for x in session.query(Attribute).all():
            if x.description:
                # If there are no descriptions, there is no point in
                # dumping attributes as there is no additional
                # information as the short names are part of node path
                raise RuntimeError("Description in an attribute")


        total = self.dfs(Node.root().lower(), lambda x: None)
        dumped = self.dfs(Node.root().lower(), self.dump)
        if total != dumped:
            raise RuntimeError("Dumped {} leafs but {} found in total".format(dumped, total))

    def dfs(self, nodes, fn):
        """
        Performs depth first search and applies fn on each leaf node
        """
        cnt = 0
        for n in nodes:
            if n.is_leaf():
                fn(n)
                cnt += 1
            else:
                cnt += self.dfs(n.lower(), fn)
        return cnt

    def dump(self, leaf):
        print(leaf.dump())
