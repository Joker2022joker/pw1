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

    def test_me(self):
        ms = range(0,6)

        for x in ms:
            m_ = "part_%s"  % x
            if hasattr(self,m_):
                print "running %s" % x
                getattr(self,"part_"+str(x))()
            else:
                print "missing %s" % x

    def part_0(self):
        """ cpk new -a ble_attr"""
        p = self.app("new -a ble_attr")
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()

        self.assertEmpty(o)
        self.assertEmpty(e)

        # ^ make sure adding attribute works
        # and then init db

        p = self.app("new -a password").wait()
        p = self.app("new -a default").wait()
        # ^ init hardcoded attributes

    def part_1(self):
        """
            cpk new ble smrt && cpk get ble smrt
        """
        p = self.app(["new","ble","smrt"])
        p.wait()

        o=p.stdout.read()
        e = p.stderr.read()

        m = re.match(r'^[a-zA-Z]{3}$',o)
        if m is None:
            print o
            print e
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

    def part_3(self):
        """ cpk new ble smrt on existing resource"""

        from commands import ResourceExists
        p = self.app(["new","ble","smrt"])
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()

        self.assertEmpty(o)
        assert(re.search(r'raise ResourceExists\(\)',e) is not None)

    def part_2(self):
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
        #o = o[:-1]
        # ^ there should not be a newline but the cpk uses correctly write(), why is that?
        e = p.stderr.read()

        if not pwd == o:
            print pwd
            print o
            raise Exception("getted value doesnt correspond to newed value")

        self.assertEmpty(e)

    def part_5(self):
        """
            cpk new ble smrt ble_attr= && cpk get ble smrt ble_attr=
        """
        p = self.app(["new","ble","smrt","ble_attr="])
        attr = "keke"
        p.stdin.write(attr)
        p.stdin.close()
        p.wait()

        self.assertEmpty(p.stdout.read())
        e = p.stderr.read()
        self.assertEmpty(e)

        p = self.app(["get","ble","smrt","ble_attr="])
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()
        self.assertEmpty(e)
        assert(o==attr)

    @classmethod
    def tearDownClass(self):
        import os
        p = self.s_app("info")
        o = p.stdout.read().split("\n")
        m = re.match(r'^db:\t(.+)$',o[0])
        db = m.groups()[0]
        check = '/tmp/cpk/'
        if len(db) > len(check) and db[0:len(check)] == check:
            os.remove(db)
 
if __name__ == '__main__':
    unittest.main()
