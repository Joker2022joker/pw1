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

        if filters[-1]['node']:
            filters.append({'attr':'password'})
            # ^ FIXME: hardcoded
            # append filter for goal we want to retrieve unless it has been specified by the user as last node

        goal = Node.get(filters)

        self.output(self.decrypt(goal.value))
