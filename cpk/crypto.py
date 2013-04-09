#! /usr/bin/env python
# -*- coding: utf-8 -*-

class Interface(object):
    def __init__(self, config=None):
        """
        :Parameters:
            config : list of (name, value)
                items of config section "crypto." + self.__class__.__name__
        """
        self.config = config

    def _encrypt(self, payload):
        """
        :Parameters:
            payload : str
        """
        raise NotImplementedError

    def _decrypt(self, payload):
        """
        :Parameters:
            payload : str
        """
        raise NotImplementedError


class Dummy(Interface):
    def _encrypt(self, payload):
        return payload

    def _decrypt(self, payload):
        return payload

try:
    import GnuPGInterface as GPGI
except ImportError:
    pass
else:
    class GnuPGInterface(Interface):
        """GNUPG cryptography adapter using GnuPGInterface project"""

        @property
        def __gpg(self):
            import GnuPGInterface
            return GnuPGInterface.GnuPG()

        def _gpg_run(args, fhs):
            gpg = self._gpg
            gpg_p = gpg.run(args,create_fhs=fhs)

            gpg_p.handles['stdin'].write(payload)
            gpg_p.handles['stdin'].close()

            out = gpg_p.handles['stdout'].read()
            gpg_p.handles['stdout'].close()

            gpg_p.wait()
            return out

        def _encrypt(self, payload):
            return self._gpg_run(['-e','--armor'], ['stdin','stdout'])

        def _decrypt(self, payload):
            return self._gpg_run(['-d','--no-tty'], ['stdin','stdout',])
