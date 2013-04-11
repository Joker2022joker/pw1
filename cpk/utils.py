#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
from inspect import isclass

from cement.core.controller import CementBaseController

SRE_ASSIGNMENT = re.compile('^((?P<var>[a-zA-Z0-9]+)=)(?P<val>.+)?$')
def tokenize_assignments(xs):
    """
    :Parameters:
        xs : list
            of strings in format var=val
    :return: dict
        with var as keys and val as the values
    """
    xs = [SRE_ASSIGNMENT.match(x) for x in xs]
    xs = [x for x in xs if x]
    xs = [x.groupdict().values() for x in xs]
    return dict(xs)

def ctrls(xs):
    return [x for x in xs if
        isclass(x) and
        x is not CementBaseController and
        issubclass(x, CementBaseController)]

class Serializable(object):
    # TODO: twisted.spread.pb.Copyable

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, dict_):
        return cls(**dict_)
