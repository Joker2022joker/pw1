#! /usr/bin/env python
# -*- coding: utf-8 -*-

class ResourceExists(Exception):
    pass

class Command(object):
    app = None

    def __call__(self):
        self._run(self.app.args)

    def _run(self):
        raise NotImplemented

    @property
    def conf(self):
        return self.app.conf

    @property
    def __u(self):
        import utils
        return utils

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
        if not self.app.args.input_kill_0x0a or not input[:-1] == "\n":
            return input
        return input[:-1]

    def output(self,s):
        if not self.app.args.output_kill_0x0a:
            print s
        else:
            import sys
            sys.stdout.write(s)
