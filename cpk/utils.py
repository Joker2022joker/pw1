#! /usr/bin/env python
# -*- coding: utf-8 -*-

def get_gpg():
    import GnuPGInterface as gnupg
    return gnupg.GnuPG()

def encrypt(s):
    gpg = get_gpg()
    gpg_p = gpg.run(['-e'],create_fhs=['stdin','stdout'])

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

    decr = gpg_p.handles['stdout'].read()[:-1]
    gpg_p.handles['stdout'].close()
    gpg_p.wait()
    
    return decr
