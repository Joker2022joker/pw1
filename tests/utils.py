#! /usr/bin/env python
# -*- coding: utf-8 -*-

from cpk.utils import ctrls
from unittest import TestCase

from cement.core.controller import CementBaseController

def test_ctrls():
    class Ctrl(CementBaseController):
        pass

    input_ = [CementBaseController, Ctrl, 1, "foo"]
    assert ctrls(input_) == [Ctrl]
