#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
from cement.core.controller import CementBaseController
from inspect import isclass

SRE_ASSIGNMENT = re.compile('^((?P<var>[a-zA-Z0-9]+)=)(?P<val>.+)?$')
def tokenize_assignments(xs):
    xs = [SRE_ASSIGNMENT.match(x) for x in xs]
    xs = [x for x in xs if x]
    xs = [x.groupdict().values() for x in xs]
    return xs


def ctrls(xs):
    return [x for x in xs if
        isclass(x) and
        x is not CementBaseController and
        issubclass(x, CementBaseController)]

