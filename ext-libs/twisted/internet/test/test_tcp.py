# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for implementations of L{IReactorTCP} and the TCP parts of
L{IReactorSocket}.
"""

from __future__ import division, absolute_import

import socket, errno
from zope.interface import implementer
from twisted.python.compat import _PY3
from twisted.python.runtime import platform
from twisted.python.failure import Failure
from twisted.python import log
from twisted.trial.unittest import SkipTest, TestCase
from twisted.internet.test.reactormixins import ReactorBuilder
from twisted.internet.error import (
    ConnectionLost, UserError, ConnectionRefusedError, ConnectionDone,
    ConnectionAborted)
from twisted.internet.interfaces import (
    ILoggingContext, IConnector, IReactorFDSet, IReactorSocket, IReactorTCP)
from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.defer import (
    Deferred, DeferredList, maybeDeferred, gatherResults)
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol
from twisted.internet.interfaces import (
    IPushProducer, IPullProducer, IHalfCloseableProtocol)
from twisted.internet.tcp import Connection, Server, _resolveIPv6

from twisted.internet.test.connectionmixins import (
    LogObserverMixin, ConnectionTestsMixin, TCPClientTestsMixin, findFreePort,
    ConnectableProtocol, EndpointCreator, runProtocolsWithReactor)
from twisted.internet.test.test_core import ObjectModelIntegrationMixin
from twisted.test.test_tcp import MyClientFactory, MyServerFactory
from twisted.test.test_tcp import ClosingFactory, ClientStartStopFactory

try:
    from OpenSSL import SSL
except ImportError:
    useSSL = False
else:
    from twisted.internet.ssl import ClientContextFactory
    useSSL = True

try:
    socket.socket(socket.AF_INET6, socket.SOCK_STREAM).close()
except socket.error as e:
    ipv6Skip = str(e)
else:
    ipv6Skip = None


if platform.isWindows():
    from twisted.internet.test import _win32ifaces
    getLinkLocalIPv6Addresses = _win32ifaces.win32GetLinkLocalIPv6Addresses
else:
    try:
        from twisted.internet.test import _posixifaces
    except ImportError:
        getLinkLocalIPv6Addresses = lambda: []
    else:
        getLinkLocalIPv6Addresses = _posixifaces.posixGetLinkLocalIPv6Addresses


def getLinkLocalIPv6Address():
    """
    Find and return a configured link local IPv6 address including a scope
    identifier using the % separation syntax.  If the system has no link local
    IPv6 addresses, raise L{SkipTest} instead.

    @raise SkipTest: if no link local address can be found or if the
        C{netifaces} module is not available.

    @return: a C{str} giving the address
    """
    addresses = getLinkLocalIPv6Addresses()
    if addresses:
        return addresses[0]
    raise SkipTest("Link local IPv6 address unavailable")


def connect(client, destination):
    """
    Connect a socket to the given destination.

    @param client: A C{socket.socket}.

    @param destination: A tuple of (host, port). The host is a C{str}, the
        port a C{int}. If the C{host} is an IPv6 IP, the address is resolved
        using C{getaddrinfo} and the first version found is used.
    """
    (host, port) = destination
    if '%' in host or ':' in host:
        address = socket.getaddrinfo(host, port)[0][4]
    else:
        address = (host, port)
    client.connect(address)


class FakeSocket(object):
    """
    A fake for L{socket.socket} objects.

    @ivar data: A C{str} giving the data which will be returned from
        L{FakeSocket.recv}.

    @ivar sendBuffer: A C{list} of the objects passed to L{FakeSocket.send}.
    """
    def __init__(self, data):
        self.data = data
        self.sendBuffer = []

    def setblocking(self, blocking):
        self.blocking = blocking

    def recv(self, size):
        return self.data

    def send(self, bytes):
        """
        I{Send} all of C{bytes} by accumulating it into C{self.sendBuffer}.

        @return: The length of C{bytes}, indicating all the data has been
            accepted.
        """
        self.sendBuffer.append(bytes)
        return len(bytes)

    def shutdown(self, how):
        """
        Shutdown is not implemented.  The method is provided since real sockets
        have it and some code expects it.  No behavior of L{FakeSocket} is
        affected by a call to it.
        """

    def close(self):
        """
        Close is not implemented.  The method is provided since real sockets
        have it and some code expects it.  No behavior of L{FakeSocket} is
        affected by a call to it.
    """

    def setsockopt(self, *args):
        """
        Setsockopt is not implemented.  The method is provided since
        real sockets have it and some code expects it.  No behavior of
        L{FakeSocket} is affected by a call to it.
    """

    def fileno(self):
        """
        Return a fake file descriptor.  If actually used, this will have no
        connection to this L{FakeSocket} and will probably cause surprising
        results.
        """
        return 1


class TestFakeSocket(TestCase):
    """
