#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from model import Node, session
from sqlalchemy.orm.exc import NoResultFound

class Command(IFace):
    def _run(self,args):
        filters = self.tokens_2_filters(self.tokenize_nodes())

        from utils import tokenize_nodes
        to_filters = self.tokens_2_filters(tokenize_nodes(self.app.args.to))

        goal = Node.get(filters)

        to = Node.get(to_filters,create=True)

        for i in goal.lower_edges:
            i.higher_node = to

        map(session.delete,goal.higher_edges)
        # ^ FIXME: there may be better solution via sqlalchemy
        session.delete(goal)
        session.commit()
