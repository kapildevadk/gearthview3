# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for twisted SSL support.
"""

import os
import errno
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import twisted.python.filepath
from twisted.trial import unittest
from twisted.internet import protocol, reactor, interfaces, defer, error
from twisted.protocols import basic
from twisted.python.runtime import platform
from twisted.test.test_tcp import ProperlyCloseFilesMixin

try:
    from OpenSSL import SSL, crypto
    from twisted.internet import ssl
    from twisted.test.ssl_helpers import ClientTLSContext, certPath
except ImportError:
    SSL = ssl = None

try:
    from twisted.protocols import tls as newTLS
except ImportError:
    newTLS = None


class UnintelligentProtocol(basic.LineReceiver):
    """
    A protocol that sends some lines and then waits for a 'READY' line to start TLS.
    """

    pretext: List[bytes]
    posttext: List[bytes]
    deferred: defer.Deferred

    def __init__(self):
        self.deferred = defer.Deferred()

    def connectionMade(self):
        for l in self.pretext:
            self.sendLine(l)

    def lineReceived(self, line: bytes):
        if line == b"READY":
            self.transport.startTLS(ClientTLSContext(), self.factory.client)
            for l in self.posttext:
                self.sendLine(l)
            self.transport.loseConnection()

    def connectionLost(self, reason: Union[defer.Deferred, error.ConnectionDone]):
        self.deferred.callback(None)


class LineCollector(basic.LineReceiver):
    """
    A protocol that collects lines and optionally initiates TLS.
    """

    doTLS: bool
    fillBuffer: bool
    deferred: defer.Deferred

    def __init__(self, doTLS: bool, fillBuffer: bool = False):
        self.doTLS = doTLS
        self.fillBuffer = fillBuffer
        self.deferred = defer.Deferred()

    def connectionMade(self):
        self.factory.rawdata = b''
        self.factory.lines = []

    def lineReceived(self, line: bytes):
        self.factory.lines.append(line)
        if line == b'STARTTLS':
            if self.fillBuffer:
                for x in range(500):
                    self.sendLine(b'X' * 1000)
            self.sendLine(b'READY')
            if self.doTLS:
                ctx = ServerTLSContext(
                    privateKeyFileName=certPath,
                    certificateFileName=certPath,
                )
                self.transport.startTLS(ctx, self.factory.server)
            else:
                self.setRawMode()

    def rawDataReceived(self, data: bytes):
        self.factory.rawdata += data
        self.transport.loseConnection()

    def connectionLost(self, reason: Union[defer.Deferred, error.ConnectionDone]):
        self.deferred.callback(None)


class SingleLineServerProtocol(protocol.Protocol):
    """
    A protocol that sends a single line of data at connectionMade.
    """

    def connectionMade(self):
        self.transport.write(b"+OK <some crap>\r\n")
        self.transport.getPeerCertificate()


class RecordingClientProtocol(protocol.Protocol):
    """
    A protocol that records the first received data.
    """

    deferred: defer.Deferred

    def __init__(self):
        self.deferred = defer.Deferred()

    def connectionMade(self):
        self.transport.getPeerCertificate()

    def dataReceived(self, data: bytes):
        self.deferred.callback(data)


class ImmediatelyDisconnectingProtocol(protocol.Protocol):
    """
    A protocol that disconnects immediately on connection.
    """

    def connectionMade(self):
        self.transport.loseConnection()


def generateCertificateObjects(organization: str, organizationalUnit: str) -> Tuple[crypto.PKey, crypto.X509Req, crypto.X509]:
    """
    Create a certificate for given organization and organizationalUnit.

    @return: a tuple of (key, request, certificate) objects.
    """
    pkey = crypto.PKey()
    pkey.generate_key(crypto.TYPE_RSA, 512)
    req = crypto.X509Req()
    subject = req.get_subject()
    subject.O = organization
    subject.OU = organizationalUnit
    req.set_pubkey(pkey)
    req.sign(pkey, "md5")

    # Here comes the actual certificate
    cert = crypto.X509()
    cert.set_serial_number(1)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(60)  # Testing certificates need not be long lived
    cert.set_issuer(req.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(pkey, "md5")

    return pkey, req, cert


def generateCertificateFiles(
