#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from . import Command as IFace
from model import Attribute, session, Node

class Command(IFace):
    def _run(self,args):
        if args.attribute:
            [ print(i.name) for i in session.query(Attribute).all()]
        else:
            if args.nodes == []:
                children = session.query(Node).filter_by(parent_id=None).all()
            else:
                n = Node.get(args.nodes)
                children = n.children

            [ print(i.name) for i in children]
