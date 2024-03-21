# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for Perspective Broker module.

TODO: update protocol level tests to use new connection API, leaving
only specific tests for old API.
"""

import sys
import os
import time
import gc
import weakref
from cStringIO import StringIO
from zope.interface import implements, Interface

from twisted.trial import unittest
from twisted.spread import pb, util, publish, jelly
from twisted.internet import protocol, main, reactor
from twisted.internet.error import ConnectionRefusedError
from twisted.internet.defer import Deferred, gatherResults, succeed
from twisted.protocols.policies import WrappingFactory
from twisted.python import failure, log
from twisted.cred.error import UnauthorizedLogin, UnhandledCredentials
from twisted.cred import portal, checkers, credentials

class Dummy(pb.Viewable):
    def view_doNothing(self, user):
        if isinstance(user, DummyPerspective):
            return 'hello world!'
        else:
            return 'goodbye, cruel world!'

class DummyPerspective(pb.Avatar):
    """
    An L{IPerspective} avatar which will be used in some tests.
    """
    def perspective_getDummyViewPoint(self):
        return Dummy()

class DummyRealm(object):
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is pb.IPerspective:
                return iface, DummyPerspective(avatarId), lambda: None

class IOPump:
    """
    Utility to pump data between clients and servers for protocol testing.

    Perhaps this is a utility worthy of being in protocol.py?
    """
    def __init__(self, client, server, clientIO, serverIO):
        self.client = client
        self.server = server
        self.clientIO = clientIO
        self.serverIO = serverIO

    def flush(self):
        """
        Pump until there is no more input or output or until L{stop} is called.
        This does not run any timers, so don't use it with any code that calls
        reactor.callLater.
        """
        # failsafe timeout
        self._stop = False
        timeout = time.time() + 5
        while not self._stop and self.pump():
            if time.time() > timeout:
                return

    def stop(self):
        """
        Stop a running L{flush} operation, even if data remains to be
        transferred.
        """
        self._stop = True

    def pump(self):
        """
        Move data back and forth.

        Returns whether any data was moved.
        """
        self.clientIO.seek(0)
        self.serverIO.seek(0)
        cData = self.clientIO.read()
        sData = self.serverIO.read()
        self.clientIO.seek(0)
        self.serverIO.seek(0)
        self.clientIO.truncate()
        self.serverIO.truncate()
        self.client.transport._checkProducer()
        self.server.transport._checkProducer()
        for byte in cData:
            self.server.dataReceived(byte)
        for byte in sData:
            self.client.dataReceived(byte)
        if cData or sData:
            return 1
        else:
            return 0

def connectedServerAndClient(realm=None):
    """
    Connect a client and server L{Broker} together with an L{IOPump}

    @param realm: realm to use, defaulting to a L{DummyRealm}

    @returns: a 3-tuple (client, server, pump).
    """
    realm = realm or DummyRealm()
    clientBroker = pb.Broker()
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(guest='guest')
    factory = pb.PBServerFactory(portal.Portal(realm, [checker]))
    serverBroker = factory.buildProtocol(('127.0.0.1',))

    clientTransport = StringIO()
    serverTransport = StringIO()
    clientBroker.makeConnection(protocol.FileWrapper(clientTransport))
    serverBroker.makeConnection(protocol.FileWrapper(serverTransport))
    pump = IOPump(clientBroker, serverBroker, clientTransport, serverTransport)
    # Challenge-response authentication:
    pump.flush()
    return clientBroker, serverBroker, pump

class SimpleRemote(pb.Referenceable):
    def remote_thunk(self, arg):
        self.arg = arg
        return arg + 1

    def remote_knuth(self, arg):
        raise Exception()

class NestedRemote(pb.Referenceable):
    def remote_getSimple(self):
        return SimpleRemote()

class SimpleCopy(pb.Copyable):
    def __init__(self):
        self.x = 1
        self.y = {"Hello":"World"}
        self.z = ['test']

class SimpleLocalCopy(pb.RemoteCopy):
    pass
pb.setUnjellyableForClass(SimpleCopy, SimpleLocalCopy)

class SimpleFactoryCopy(pb.Copyable):
    """
    @cvar allIDs: hold every created instances of this class.
    @type allIDs: C{dict}
    """
    allIDs = {}
    def __init__(self, id):
        self.id = id
        SimpleFactoryCopy.allIDs[id] = self

def createFactoryCopy(state):
    """
    Factory of L{SimpleFactoryCopy}, getting a created instance given the
    C{id} found in C{state}.
    """
    stateId = state.get("id", None)
    if stateId is None:
        raise RuntimeError("factory copy state has no 'id' member %s" %
                           (repr(state),))
    if not stateId in SimpleFactoryCopy.allIDs:
       
