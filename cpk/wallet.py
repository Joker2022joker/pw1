#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from twisted.protocols.basic import LineReceiver
from twisted.internet.error import ConnectionDone

import json

from .xdg import save_data_path
from .utils import Serializable

class Service(Serializable):
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


class WalletProtocol(LineReceiver):
    """
    :ivar wallet: `cpk.wallet.Wallet`
    :ivar adapter: `cpk.crypto.Interface`
    :ivar header:
    """
    delimiter = b'\n\n'

    def __init__(self, wallet, adapter):
        self.wallet = wallet
        self.adapter = adapter
        self.read_header = True

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

    def lineReceived(self, line):
        line = line.decode('utf-8')
        line = self.adapter.decrypt(line)
        line = json.loads(line)
        if self.read_header:
            self.headerReceived(line)
            self.read_header = False
            return

        self.recordReceived(line)

    def headerReceived(self, header):
        """
        :Parameters:
            header : dict
        """
        if 'services' in header:
            for s in header['services']:
                self.serviceReceived(s)

    def serviceReceived(self, s):
        s = Service.from_dict(s)
        self.wallet.add_service(s)

    def recordReceived(self, line):
        pass

class Wallet(object):
    """
    :ivar adapter: `crypto.Interface`
    :ivar services: dict of `Service.name` -> `Service`
    """
    def __init__(self, adapter):
        """
        :Parameters:
            adapter : `crypto.Interface`
        """
        self.adapter = adapter
        self.services = {}

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
        p = WalletProtocol(self, self.adapter)
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

    def add_service(self, service):
        """
        :Parameters:
            service : `Service`
        """
        if service.name in self.services:
            raise RuntimeError("Duplicit service {0}".format(service.name))

        self.services[service.name] = service
