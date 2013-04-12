#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from copy import deepcopy
import logging

from twisted.protocols.basic import LineReceiver
from twisted.internet.error import ConnectionDone

import json

from .xdg import save_data_file
from .utils import Serializable

log = logging.getLogger(__name__)

class LineRecord(object):
    """
    :ivar raw:
        raw encrypted record
    """
    raw = None

    def changed(self):
        """
        Called when LineRecord is changed
        """
        self.raw = None

class Header(LineRecord, Serializable):
    """
    :ivar services: dict of `Service.name` -> `Service`
    """
    def __init__(self, w):
        self.services = {}
        self.wallet = w
        self.wallet._header = self
        # NOTE: ^ this is weird

    def to_dict(self):
        return {'services': [x.to_dict() for x in self.services.values()]}

    @classmethod
    def from_dict(cls, d, wallet):
        h = cls(wallet)
        for s in d['services']:
            h.add_service(Service.from_dict(s, wallet))

        return h

    def add_service(self, service):
        """
        :Parameters:
            service : `Service`
        """
        if service.name in self.services:
            raise RuntimeError("Duplicit service {0}".format(service.name))

        self.services[service.name] = service
        if self.wallet._loaded:
            self.changed()

    def __eq__(self, other):
        return self.services == other.services

class Service(Serializable):
    def __init__(self, name, id_as=[], password_as=[]):
        # FIXME: id_as makes sense to be [] but password_as must be non-empty
        # list
        # ∴ FIXME: the order should also be reversed: 1st passwords, then
        # identificators
        """
        :Parameters:
            name : str
                service name
            id_ts : list of str
                service identification attribute names
            password_as : list of str
                password attribute names for this service
        """
        for i in password_as:
            if i in id_as:
                raise ValueError("{0} attribute found in both password and"
                    " identification attributes".format(i))

        self.name, self.id_as, self.password_as = name, id_as, password_as

    def __contains__(self, key):
        return key in self.id_as or key in self.password_as

    def __eq__(self, other):
        return self.name == other.name \
            and self.id_as == other.id_as \
            and self.password_as == other.password_as

class Record(LineRecord, Serializable):
    """
    :ivar service: `Service`
    :ivar attrs: dict
        str -> str
    """
    def __init__(self, service, **attributes):
        """
        :Parameters:
            service : `Service`
        """
        if not isinstance(service, Service):
            raise TypeError("Expected {0} got {1}".
                format(Service, service.__class__))

        self.service = service
        self.attrs = {}
        for name,value in attributes.items():
            self.add_attribute(name, value)

    def add_attribute(self, name, value):
        """
        :Parameters:
            name : str
            value : str
        """
        if not name in self.service:
            raise ValueError("Attribute {0} not in {1}".
                format(name, self.service))

        self.attrs[name] = value

    def to_dict(self):
        d = deepcopy(self.__dict__)
        d['service'] = self.service.name
        # FIXME: the service shenanigans feel wrong.
        # The Record can be serialized just by itself, but to be deserialized
        # it need's extra work as in WalletProtocol.recordReceived
        # also tests.wallet.TestRecord
        return d

    @classmethod
    def from_dict(cls, d, wallet):
        d['service'] = wallet.get_service(d['service'])
        return cls(d['service'], **d['attrs'])

    def __eq__(self, other):
        return self.service == other.service \
            and self.attrs == other.attrs

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
        self._line_records_sent = 0

    def _get_buffer(self): # pragma: no cover # TODO
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
        if not reason == ConnectionDone:
            raise RuntimeError('This should never happen as we are feeding'
                ' this protocol from a file')

        self.wallet.loaded()

    def lineReceived(self, line):
        raw_line = line.decode('utf-8')
        line = self.adapter.decrypt(raw_line)
        line = json.loads(line)
        if not self.wallet._header:
            return self._headerDictReceived(line)

        r = Record.from_dict(line, self.wallet)
        r.raw = raw_line
        self.recordReceived(r)

    def _headerDictReceived(self, d):
        Header.from_dict(d, self.wallet)

    def recordReceived(self, r):
        """
        :Parameters:
            s : `Record`
        """
        self.wallet.add_record(r)

    def _sendLineRecord(self, record):
        """
        :Parameters:
            record : LineRecord
        """
        line = record.to_dict()
        line = json.dumps(line)
        line = self.adapter.encrypt(line)
        self.sendLine(line)

    def sendLineRecord(self, record):
        """
        If record has changed it is sent through _sendLineRecord for full
        serialization/crypto stuff.
        Otherwise old crypto record is sent straight to the transport via
        sendLine

        :Parameters:
            record : LineRecord
        """
        if isinstance(record, Header) and self._line_records_sent > 0:
            raise RuntimeError("someone fucked up")

        if record.raw:
            self.sendLine(record.raw)
        else:
            self._sendLineRecord(record)

        self._line_records_sent += 1

class Wallet(object):
    """
    :ivar adapter: `crypto.Interface`
    :ivar records: list of `Record`
    :ivar _loaded: bool
        see Wallet.loaded()
    """
    protocol = WalletProtocol

    def __init__(self, adapter):
        """
        :Parameters:
            adapter : `crypto.Interface`
        """
        self.adapter = adapter
        self.records = []
        self._loaded = False
        self._header = None
        self._record_changed = False

    def _open(self, file_):
        """
        :Parameters:
            file : str
                absolute path to the wallet file
        """
        log.debug("opening wallet from %s", file_)
        if not os.path.exists(file_):
            return self.loaded() # TODO: unit

        if not os.path.isfile(file_):
            raise RuntimeError('wallet file is not a file {0}'.format(file_))

        wfile = open(file_, 'rb')
        p = self.protocol(self, self.adapter)
        p.dataReceived(wfile.read())
        p.connectionLost()

    @staticmethod
    def open(name, crypto_adapter):
        """
        Return new Wallet object from XDG_DATA_HOME/`name` accessed via
        `crypto_adapter`

        :Parameters:
            name : str
                filename of the wallet file. It is expected in
                $XDG_DATA_HOME/cpk
            crypto_adapter : `cpk.crypto.Interface`
                cryptographic adapter used for actual reading/writing from/to
                wallet file
        :return: Wallet
        """

        w = Wallet(crypto_adapter)
        w._open(save_data_file(name))
        return w

    def record_changed(self):
        for r in self.records:
            if not r.raw:
                return True

        return False

    def close(self):
        """
        Close the wallet, saving any changes that have been made
        """
        if self._header.raw and not self.record_changed():
            return

        self._close()

    def _close(self):
        wtmpfile = save_data_file("wallet.tmp")
        p = WalletProtocol(self, self.adapter)
        p.transport = open(wtmpfile, 'w')

        p.sendLineRecord(self._header)
        for x in self.records:
            p.sendLineRecord(x)

    def add_service(self, service):
        if self._loaded and not self._header:
            Header(self) # TODO: unit

        self._header.add_service(service)

    def get_service(self, service):
        """
        :Parameters:
            service : str
                `Service.name`

        :raise KeyError: when service doesn't exist
        """
        return self._header.services[service]

    @property
    def services(self):
        return self._header.services

    def add_record(self, record):
        self.records.append(record)

    def loaded(self):
        """
        Called when wallet has been loaded from "storage" and further changes
        make modifications against the persisted wallet
        """
        self._loaded = True
