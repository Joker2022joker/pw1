#! /usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
import re
from cement.core.controller import CementBaseController
from inspect import isclass

class PythonGnupg:
    """Cryptography adapter for gnupg using python-gnupg project"""

    @property
    def _gpg(self):
        import gnupg
        return gnupg.GPG()

    def encrypt(self, s):
        # doesnt seem to be working with defalt-recipient-self
        return str(self._gpg.encrypt(s, None))
        # ^ FIXME: this needs to be configurable

    def decrypt(self, s):
        return str(self._gpg.decrypt(s))

class PyGnupg:
    """Cryptography adapter for gnupg using py-gnupg project"""

    @property
    def _gpg(self):
        import GnuPGInterface
        return GnuPGInterface.GnuPG()

    def encrypt(self, s):
        gpg = self._gpg
        gpg_p = gpg.run(['-e','--armor'],create_fhs=['stdin','stdout'])

        gpg_p.handles['stdin'].write(s)
        gpg_p.handles['stdin'].close()

        enc = gpg_p.handles['stdout'].read()
        gpg_p.handles['stdout'].close()

        gpg_p.wait()

        return enc

    def decrypt(self, enc):
        gpg = self._gpg
        gpg_p = gpg.run(['-d','--no-tty'],create_fhs=['stdin','stdout','stderr'])
        gpg_p.handles['stdin'].write(enc)

        gpg_p.handles['stdin'].close()

        decr = gpg_p.handles['stdout'].read()
        gpg_p.handles['stdout'].close()
        gpg_p.wait()

        return decr

impl = PyGnupg()

def encrypt(s):
    return impl.encrypt(s)

def decrypt(enc):
    return impl.decrypt(enc)

def tokenize_nodes(nodes):
    """
        tokenize list of nodes in format attribute=value into list of (attribute,value).
    """
    from cpk.model import Attribute, session
    attrs = [i.name for i in session.query(Attribute).all()]

    sre_parse_nodes = '^((?P<node_type>%s)=)?(?P<node_name>.+)?$' % "|".join(attrs)
    getLogger("%s" % (__name__,)).debug(sre_parse_nodes)
    sre_parse_nodes = re.compile(sre_parse_nodes)

    getLogger("%s" % (__name__,)).debug("tokenizer input: %s" % nodes)
    tokens = [sre_parse_nodes.match(i).groupdict().values()
        for i in nodes]

    getLogger("%s" % (__name__,)).debug("tokens: %s" % tokens)
    return tokens

SRE_ASSIGNMENT = re.compile('^((?P<var>[a-zA-Z0-9]+)=)(?P<val>.+)?$')
def tokenize_assignments(xs):
    xs = [SRE_ASSIGNMENT.match(x) for x in xs]
    xs = [x for x in xs if x]
    xs = [x.groupdict().values() for x in xs]
    return xs


def ctrls(xs):
    return [x for x in xs if
        isclass(x) and
        x is not CementBaseController and
        issubclass(x, CementBaseController)]

