import datetime
import decimal

from zope.interface import implements, verifyClass, verifyObject
from zope.interface.verify import verifyClass, verifyObject

from twisted.python import filepath
from twisted.python.failure import Failure
from twisted.protocols import amp
from twisted.trial import unittest
from twisted.internet import protocol, defer, error, reactor, interfaces
from twisted.test import iosim
from twisted.test.proto_helpers import StringTransport

try:
    from twisted.internet import ssl
except ImportError:
    ssl = None

if ssl and not ssl.supported:
    ssl = None

if ssl is None:
    skipSSL = "SSL not available"
else:
    skipSSL = None


class TestProto(protocol.Protocol):
    """
    A trivial protocol for use in testing where a L{Protocol} is expected.

    @ivar instanceId: the id of this instance
    @ivar onConnLost: deferred that will fired when the connection is lost
    @ivar dataToSend: data to send on the protocol
    """

    instanceCount = 0

    def __init__(self, onConnLost, dataToSend):
        self.onConnLost = onConnLost
        self.dataToSend = dataToSend
        self.instanceId = TestProto.instanceCount
        TestProto.instanceCount += 1

    def connectionMade(self):
        self.data = []
        self.transport.write(self.dataToSend)

    def dataReceived(self, bytes):
        self.data.append(bytes)

    def connectionLost(self, reason):
        self.onConnLost.callback(self.data)

    def __repr__(self):
        """
        Custom repr for testing to avoid coupling amp tests with repr from
        L{Protocol}

        Returns a string which contains a unique identifier that can be looked
        up using the instanceId property::

            <TestProto #3>
        """
        return "<TestProto #%d>" % (self.instanceId,)


class SimpleSymmetricProtocol(amp.AMP):

    def sendHello(self, text):
        return self.callRemoteString(
            "hello",
            hello=text)

    def amp_HELLO(self, box):
        return amp.Box(hello=box['hello'])

    def amp_HOWDOYOUDO(self, box):
        return amp.QuitBox(howdoyoudo='world')


class UnfriendlyGreeting(Exception):
    """Greeting was insufficiently kind.
    """


class DeathThreat(Exception):
    """Greeting was insufficiently kind.
    """


class UnknownProtocol(Exception):
    """Asked to switch to the wrong protocol.
    """


class TransportPeer(amp.Argument):
    # this serves as some informal documentation for how to get variables from
    # the protocol or your environment and pass them to methods as arguments.
    def retrieve(self, d, name, proto):
        return ''

    def fromStringProto(self, notAString, proto):
        return proto.transport.getPeer()

    def toBox(self, name, strings, objects, proto):
        return


class Hello(amp.Command):

    commandName = 'hello'

    arguments = [('hello', amp.String()),
                 ('optional', amp.Boolean(optional=True)),
                 ('print', amp.Unicode(optional=True)),
                 ('from', TransportPeer(optional=True)),
                 ('mixedCase', amp.String(optional=True)),
                 ('dash-arg', amp.String(optional=True)),
                 ('underscore_arg', amp.String(optional=True))]

    response = [('hello', amp.String()),
                ('print', amp.Unicode(optional=True))]

    errors = {UnfriendlyGreeting: 'UNFRIENDLY'}

    fatalErrors = {DeathThreat: 'DEAD'}


class NoAnswerHello(Hello):
    commandName = Hello.commandName
    requiresAnswer = False


class FutureHello(amp.Command):
    commandName = 'hello'

    arguments = [('hello', amp.String()),
                 ('optional', amp.Boolean(optional=True)),
                 ('print', amp.Unicode(optional=True)),
                 ('from', TransportPeer(optional=True)),
                 ('bonus', amp.String(optional=True)), # addt'l arguments
                                                       # should generally be
                                                       # added at the end, and
                                                       # be optional...
                 ]

    response = [('hello', amp.String()),
                ('print', amp.Unicode(optional=True))]

    errors = {UnfriendlyGreeting: 'UNFRIENDLY'}


class WTF(amp.Command):
    """
    An example of an invalid command.
    """


class BrokenReturn(amp.Command):
    """ An example of a perfectly good command, but the handler is going to return
    None...
    """

    commandName = 'broken_return'

class Goodbye(amp.Command):
    # commandName left blank on purpose: this tests implicit command names.
    response = [('goodbye', amp.String())]
    responseType = amp.QuitBox

class Howdoyoudo(amp.Command):
    commandName = 'howdoyoudo'
    # responseType = amp.QuitBox

class WaitForever(amp.Command):
    commandName = 'wait_forever'

class GetList(amp.Command):
    commandName = 'getlist'
    arguments = [('length', amp.Integer())]
    response = [('body', amp.AmpList([('x', amp.Integer())]))]

class DontRejectMe(amp.Command):
    commandName = 'dontrejectme'
    arguments = [
            ('magicWord', amp.Unicode()),
            ('list', amp.AmpList(
