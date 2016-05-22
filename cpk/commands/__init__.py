#! /usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger

class ResourceExists(Exception):
    pass

class Command(object):
    app = None

    def __call__(self):
        self._run(self.app.args)

    def _run(self):
        raise NotImplemented

    def tokenize_nodes(self):
        from cpk.utils import tokenize_nodes
        return tokenize_nodes(self.app.args.nodes)

    def tokens_2_filters(self,tokens):
        tokens = [[y for y in x] for x in tokens]
        return [{"attr":x, "node":y} for x,y in tokens]

    @property
    def conf(self):
        return self.app.conf

    @property
    def args(self):
        return self.app.args

    @property
    def __u(self):
        import cpk.utils
        return cpk.utils

    def encrypt(self,p):
        if not self.conf.getboolean('debug','encrypt'):
            return p
        else:
            return self.__u.encrypt(p)

    def decrypt(self,p):
         if not self.conf.getboolean('debug','encrypt'):
            return p
         else:
            return self.__u.decrypt(p)

    def input(self):
        import sys
        input=sys.stdin.read()
        if not self.conf.getboolean('main','input_kill_0x0a') or not input[-1] == "\n":
            return input
        return input[:-1]

    def die(self,message):
        import sys
        print(message, file=sys.stderr)
        from logging import getLogger
        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).fatal(message)
        exit(1)

    def output(self,s):
        if not self.conf.getboolean('main','output_kill_0x0a'):
            print(s)
        else:
            import sys
            sys.stdout.write(s)
