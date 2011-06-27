#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from model import Attribute, session

class Command(IFace):
    def _run(self,args):
        if args.attribute:
            print [i.name for i in session.query(Attribute).all()]
        else:
            raise NotImplementedError()
