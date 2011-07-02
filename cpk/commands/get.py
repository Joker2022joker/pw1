#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from model import Attribute, Node
from sqlalchemy.orm.exc import NoResultFound

class Command(IFace):
    def _run(self,args):
        if self.args.attribute:
            return self.attribute()

        filters = self.tokens_2_filters(self.tokenize_nodes())

        if filters[-1]['node']:
            try:
                a = Attribute.password()
                filters.append({'attr':a.name})
                # append filter for goal we want to retrieve
                # unless it has been specified by the user as the last node
                # or there is no configured password attribute

            except NoResultFound:
                filters.append({})
                # append empty filter so we'll get the "one more" node

        goal = Node.get(filters)

        self.output(self.decrypt(goal.value))
