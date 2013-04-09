#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from .xdg import save_data_path

class Service(object):
    def __init__(self, name, id_as, password_as):
        """
        :Parameters:
            name : str
                service name
            id_ts : list of str
                service identification attribute names
            password_as : list of str
                password attribute names for this service
        """
        self.name, self.id_as, self.password_as = name, id_as, password_as


from twisted.protocols.basic import LineReceiver
from twisted.internet.error import ConnectionDone

class WalletProtocol(LineReceiver):
    """
    :ivar wallet: `cpk.wallet.Wallet`
    """
    delimiter = b'\n\n'

    def __init__(self, wallet):
        self.wallet = wallet

    def _get_buffer(self):
        if hasattr(self, '_buffer'):
            # twisted >= 13
            return self._buffer

        return self._LineReceiver__buffer
        # twisted < 13

    def connectionLost(self, reason=ConnectionDone):
        if self._get_buffer():
            raise RuntimeError('Unprocessed data still in the buffer')
    # NOTE: not sure if it is cool to just pass the buffer into lineReceived on
    # connectionLost when reason = ConnectionDone
    # so I'm just gonna require all lines MUST be ended with the delimiter for
    # now

class Wallet(object):
    """
    :ivar adapter: `crypto.Interface`
    """
    def __init__(self, adapter):
        """
        :Parameters:
            adapter : `crypto.Interface`
        """
        self.adapter = adapter

    def _open(self, file_):
        """
        :Parameters:
            file : str
                absolute path to the wallet file
        """
        if not os.path.exists(file_):
            return

        if not os.path.isfile(file_):
            raise RuntimeError('wallet file is not a file {0}'.format(file_))

        wfile = open(file_, 'rb')
        p = WalletProtocol(self)
        p.dataReceived(wfile.read())
        p.connectionLost()


    @staticmethod
    def open(name, crypto_adapter):
        """
        :Parameters:
            name : str
                filename of the wallet file. It is expected in
                $XDG_DATA_HOME/cpk
            crypto_adapter : `cpk.crypto.Interface`
                cryptographic adapter used for actual reading/writing from/to
                wallet file
        :
        """

        w = Wallet(crypto_adapter)
        w._open(os.path.join(save_data_path(),name))
        return w
