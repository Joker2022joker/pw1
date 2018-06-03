#! /usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
import subprocess

class ShellGnupg:
    def decrypt(self, ciphertext):
        return self._gpg(["gpg", "-d"], ciphertext)

    def encrypt(self, plaintext):
        return self._gpg("gpg -ea", plaintext)

    def _gpg(self, args, stdin):
        p = subprocess.Popen(
            args
        ,   stdout = subprocess.PIPE
        ,   stdin = subprocess.PIPE
        ,   shell = True
        )
        out, err = p.communicate(input=stdin.encode("utf-8"))
        if p.returncode != 0:
            raise RuntimeError("GPG error {}: {}".format(p.returncode, err))
        return out.decode("utf-8")

impl = ShellGnupg()

def encrypt(s):
    return impl.encrypt(s)

def decrypt(enc):
    return impl.decrypt(enc)

def tokenize_nodes(nodes):
    """
        tokenize list of nodes in format attribute=value into list of (attribute,value).
    """
    import re
    from cpk.model import Attribute, session
    attrs = [i.name for i in session.query(Attribute).all()]

    sre_parse_nodes = '^((?P<node_type>%s)=)?(?P<node_name>.+)?$' % "|".join(attrs)
    getLogger("%s" % (__name__,)).debug(sre_parse_nodes)
    sre_parse_nodes = re.compile(sre_parse_nodes)

    getLogger("%s" % (__name__,)).debug("tokenizer input: %s" % nodes)
    tokens = [sre_parse_nodes.match(i).groupdict() for i in nodes]
    tokens = [(t["node_type"], t["node_name"]) for t in tokens]

    getLogger("%s" % (__name__,)).debug("tokens: %s" % tokens)
    return tokens

