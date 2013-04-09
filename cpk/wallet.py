#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

class Wallet(object):
    def __init__(self, adapter):
        self.adapter = adapter

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

        wallet_file = save_data_path(name)
        crypto_adapter.open(wallet_file)
        w = Wallet(crypto_adapter)
        # w.load()
        return w
