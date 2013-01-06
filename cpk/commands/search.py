#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from cpk.model import Attribute, Node, session
from sqlalchemy.orm.exc import NoResultFound

def make_token(n):
    if n.attr.name:
        return '%s=%s' % (n.attr.name, n.value)
    else:
        return '%s' % n.value

class Command(IFace):
    def _run(self,args):
        #nodes = session.query(Node).filter_by(value=args.node_value).all()
        nodes_found = Node.query().get_nodes_by_value(args.node_value).all()
        if not nodes_found:
            print "No matches"
            return

        for nf in nodes_found:
            for path in nf.get_paths():
                path_formatted = [make_token(n) for n in path]
                print " ".join(path_formatted)
