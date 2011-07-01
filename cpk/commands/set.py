#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from model import NoNode, Node, session, Attribute
import sys

class Command(IFace):
    def _run(self,args):
        filters = self.tokens_2_filters(self.tokenize_nodes())

        n = Node.get(filters)

        n.value = self.encrypt(self.input())
        session.commit()
