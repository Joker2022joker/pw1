#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from cpk.model import Node, session
from sqlalchemy.orm.exc import NoResultFound

class Command(IFace):
    def _run(self,args):
        filters = self.tokens_2_filters(self.tokenize_nodes())

        # do not modify filters here
        # in this command the path must be specified exactly

        goal = Node.get(filters)

        if not goal.lower() == []:
            raise Exception('node is not leaf')
            # ^ FIXME add -r option

        map(session.delete,goal.higher_edges)
        # ^ FIXME: there may be better solution via sqlalchemy
        session.delete(goal)
        session.commit()
