#! /usr/bin/env python
# -*- coding: utf-8 -*-

class Interface(object):
    """
    :ivar wallet: file
        open wallet file
    """
    def __init__(self, config):
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

    def open(self, path):
        """
        :Parameters:
            path : str
                absolute path to the wallet file
        """
        self.wallet = open(path)

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
