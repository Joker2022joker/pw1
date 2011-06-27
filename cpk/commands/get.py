#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from model import Password, AttributeValue

class Command(IFace):
    def _run(self,args):
        if args.attribute:
            av = AttributeValue.get(args.attribute,args.nodes)
            print av.value
        else:
            pwd = Password.get(args.nodes)
            self.output(self.decrypt(pwd.password))
