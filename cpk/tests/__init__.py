#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import re

from os.path import dirname,abspath,join
sys.path.insert(0,abspath(dirname(dirname(__file__))))

from app import App,ConfParser

from subprocess import Popen,PIPE
class ShouldbeEmpty(Exception):
    pass

class TestClass(unittest.TestCase):
    @staticmethod
    def cpk():
        return join(abspath(dirname(dirname(__file__))),"cpk.py")

    def assertEmpty(self,v):
        if not v == "":
            print v
            raise ShouldbeEmpty(v)

    @classmethod
    def s_app(self,cmd):
        if type(cmd) is str:
            cmd = cmd.split(" ")

        cmd.insert(0,self.cpk())

        p = Popen(cmd,0,stdin=PIPE,stderr=PIPE,stdout=PIPE)
        return p

    def app(self,cmd):
        return TestClass.s_app(cmd)

    def test_a(self):
        """
            cpk new ble smrt && cpk get ble smrt
        """
        p = self.app(["new","ble","smrt"])
        p.wait()

        o=p.stdout.read()
        e = p.stderr.read()

        m = re.match(r'^[a-zA-Z]{3}$',o)
        if m is None:
            raise Exception(o)

        expect = o

        self.assertEmpty(e)
        
        p = self.app("get ble smrt")
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()

        if not expect == o:
            raise Exception("getted value doesnt correspond to newed value")

        self.assertEmpty(e)

    def test_c(self):
        """ cpk new ble smrt on existing resource"""
        # ^ this does not work as a separate test
        # - the resource does not appear to be existing and so i written
        # why?
        from commands import ResourceExists
        p = self.app(["new","ble","smrt"])
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()

        self.assertEmpty(o)
        assert(re.search(r'raise ResourceExists\(\)',e) is not None)

    def test_d(self):
        """ cpk new -a ble_attr"""
        p = self.app("new -a ble_attr")
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()

        self.assertEmpty(o)
        self.assertEmpty(e)

    def test_b(self):
        """
            cpk new --stdin ble smrt2 && cpk get ble smrt2
        """
        p = self.app(["new","--stdin","ble","smrt2"])
        pwd = "he3"
        p.stdin.write(pwd+"\n")
        p.stdin.close()
        p.wait()
        o=p.stdout.read()
        self.assertEmpty(o)

        e = p.stderr.read()
        self.assertEmpty(e)
        
        p = self.app("get ble smrt2")
        p.wait()
        o = p.stdout.read()
        o = o[:-1]
        # ^ there should not be a newline but the cpk uses correctly write(), why is that?
        e = p.stderr.read()

        if not pwd == o:
            raise Exception("getted value doesnt correspond to newed value")

        self.assertEmpty(e)

    def test_e(self):
        """
            cpk set -a ble ble smrt && cpk get -a ble ble smrt
        """
        p = self.app(["set","-a","ble_attr","ble","smrt"])
        attr = "keke"
        p.stdin.write(attr)
        p.stdin.close()
        p.wait()

        self.assertEmpty(p.stdout.read())
        e = p.stderr.read()
        self.assertEmpty(e)

        p = self.app(["get","-a","ble_attr","ble","smrt"])
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()
        self.assertEmpty(e)
        o = o[:-1]
        assert(o==attr)

    @classmethod
    def tearDownClass(self):
        import os
        p = self.s_app("info")
        o = p.stdout.read()
        m = re.search(r'^db:\t(.+)$',o)
        db = m.groups()[0]
        check = '/tmp/cpk/'
        if len(db) > len(check) and db[0:len(check)] == check:
            os.remove(db)
 
if __name__ == '__main__':
    unittest.main()
