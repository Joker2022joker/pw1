#! /usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger

def get_gpg():
    import GnuPGInterface as gnupg
    return gnupg.GnuPG()

def encrypt(s):
    gpg = get_gpg()
    gpg_p = gpg.run(['-e','--armor'],create_fhs=['stdin','stdout'])

    gpg_p.handles['stdin'].write(s)
    gpg_p.handles['stdin'].close()

    enc = gpg_p.handles['stdout'].read()
    gpg_p.handles['stdout'].close()

    gpg_p.wait()

    return enc

def decrypt(enc):
    gpg = get_gpg()
    gpg_p = gpg.run(['-d','--no-tty'],create_fhs=['stdin','stdout','stderr'])
    gpg_p.handles['stdin'].write(enc)

    gpg_p.handles['stdin'].close()

    decr = gpg_p.handles['stdout'].read()
    gpg_p.handles['stdout'].close()
    gpg_p.wait()
    
    return decr

def tokenize_nodes(nodes):
    """
        tokenize list of nodes in format attribute=value into list of (attribute,value).
    """
    import re
    from model import Attribute, session
    attrs = [i.name for i in session.query(Attribute).all()]
    
    sre_parse_nodes = '^((?P<node_type>%s)=)?(?P<node_name>.+)?$' % "|".join(attrs)
    getLogger("%s" % (__name__,)).debug(sre_parse_nodes)
    sre_parse_nodes = re.compile(sre_parse_nodes)

    getLogger("%s" % (__name__,)).debug("tokenizer input: %s" % nodes)
    tokens = [sre_parse_nodes.match(i).groupdict().values()
        for i in nodes]

    getLogger("%s" % (__name__,)).debug("tokens: %s" % tokens)
    return tokens

