#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from cpk.utils import tokenize_assignments, ctrls
from unittest import TestCase

from cement.core.controller import CementBaseController
from nose.tools import eq_

def test_ctrls():
    class Ctrl(CementBaseController):
        pass

    input_ = [CementBaseController, Ctrl, 1, "foo"]
    eq_(ctrls(input_), [Ctrl])

def test_tokenize_assignments():
    input_ = ['aZ0=b.,:/', 'x=d=e']
    output = [['aZ0', 'b.,:/'], ['x', 'd=e']]

    eq_(tokenize_assignments(input_), output)
