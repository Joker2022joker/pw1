#! /usr/bin/env python
# -*- coding: utf-8 -*-

class MatchedMultiple(Exception):
    def __init__(self, matched, last):
        self.matched = matched
        self.last = last

