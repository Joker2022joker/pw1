#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from model import Attribute, Node

class Command(IFace):
    def attribute(self):
        a = Attribute.get(self.args.nodes[0])
        print a.name

    def _run(self,args):
        if self.args.attribute:
            return self.attribute()

        filters = self.tokens_2_filters(self.tokenize_nodes())
        filters.append({'attr':'password'})
        # ^ FIXME: hardcoded

        pwd = Node.get(filters)
        self.output(self.decrypt(pwd.value))
