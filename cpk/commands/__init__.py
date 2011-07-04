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
        import re
        from model import Attribute, session
        attrs = [i.name for i in session.query(Attribute).all()]
        
        sre_parse_nodes = '^((?P<node_type>%s)=)?(?P<node_name>[a-zA-Z0-9@.-]+)?$' % "|".join(attrs)
        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(sre_parse_nodes)
        sre_parse_nodes = re.compile(sre_parse_nodes)

        tokens = [sre_parse_nodes.match(i).groupdict().values()
            for i in self.app.args.nodes]
        # ^ FIXME raises AttributeError on syntax error
        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(tokens)
        return tokens

    def tokens_2_filters(self,tokens):
        return map(lambda (x,y): {"attr":x, "node":y}, tokens)

    @property
    def conf(self):
        return self.app.conf

    @property
    def args(self):
        return self.app.args

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
        if not self.conf.getboolean('main','input_kill_0x0a') or not input[-1] == "\n":
            return input
        return input[:-1]

    def die(self,message):
        import sys
        print >> sys.stderr, message
        from logging import getLogger
        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).fatal(message)
        exit(1)

    def output(self,s):
        if not self.conf.getboolean('main','output_kill_0x0a'):
            print s
        else:
            import sys
            sys.stdout.write(s)
