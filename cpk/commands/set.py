#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from model import NoNode, Password, Node, session, AttributeValue, Attribute
import sys

class Command(IFace):
    def _run(self,args):
        if args.attribute:
            av = AttributeValue.get(args.attribute,args.nodes,create=True)
            av.value = self.input()
            session.add(av)
        else:
            p = Password.get(args.nodes)
            p.password = self.encrypt(self.input())
            session.add(p)

        session.commit()
