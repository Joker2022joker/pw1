#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import re, logging, os
log = logging.getLogger(__name__)

from os.path import dirname,abspath,join,expanduser
sys.path.insert(0,abspath(dirname(dirname(__file__))))

from cpk.app import App,ConfParser

from subprocess import Popen,PIPE
class ShouldbeEmpty(Exception):
    pass

class TestClass(unittest.TestCase):
    @staticmethod
    def cpk():
        return join(abspath(dirname(dirname(__file__))),"cpk")

    def assertEmpty(self,v):
        self.assertEquals(v, "")

    @classmethod
    def s_app(self,cmd):
        if type(cmd) is str:
            cmd = cmd.split(" ")

        cmd.insert(0,"cpk")
        log.debug(cmd)
        p = Popen(cmd,0,stdin=PIPE,stderr=PIPE,stdout=PIPE)
        return p

    def app(self,cmd):
        return TestClass.s_app(cmd)

    def setUp(self):
        base_path = expanduser("~/.config/cpk")
        if not os.path.isdir(base_path):
            os.makedirs(base_path)
        f = open(join(base_path, "config.ini"),"w")
        f.write("[main]\n"
            "password_generator = apg -n 1 -m 5 -x 5\n"
            "[attributes]\n"
            "password = p\n"
        )
        f.close()

    def tearDown(self):
        pass
        os.unlink(expanduser("~/.config/cpk/config.ini"))
        os.unlink(expanduser("~/.local/share/cpk/wallet.asc"))

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
        m = re.match(r'^.{5}$',o)
        self.assertTrue(m)
        expect = o

        e = p.stderr.read()
        self.assertEmpty(e)

        p = self.app("get ble smrt")
        p.wait()
        o = p.stdout.read()
        e = p.stderr.read()

        self.assertEqual(expect, o)
        self.assertEmpty(e)

    def part_3(self):
        """ cpk new ble smrt on existing resource"""

        from cpk.commands import ResourceExists
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

        self.assertEqual(pwd, o)
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

if __name__ == '__main__':
    unittest.main()
