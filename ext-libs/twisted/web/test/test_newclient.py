# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.web._newclient}.
"""

import unittest
from unittest.mock import Mock, patch
from contextlib import ExitStack
from twisted.python import log
from twisted.python.failure import Failure
from twisted.internet.interfaces import IConsumer, IPushProducer
from twisted.internet.error import ConnectionDone, ConnectionLost
from twisted.internet.defer import Deferred, succeed, fail
from twisted.internet.protocol import Protocol
from unittest.mock import PropertyMock
from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport, AccumulatingProtocol
from twisted.web._newclient import UNKNOWN_LENGTH, STATUS, HEADER, BODY, DONE
from twisted.web._newclient import Request, Response, HTTPParser, HTTPClientParser
from twisted.web._newclient import BadResponseVersion, ParseError, HTTP11ClientProtocol
from twisted.web._newclient import ChunkedEncoder, RequestGenerationFailed
from twisted.web._newclient import RequestTransmissionFailed, ResponseFailed
from twisted.web._newclient import WrongBodyLength, RequestNotSent
from twisted.web._newclient import ConnectionAborted, ResponseNeverReceived
from twisted.web._newclient import BadHeaders, ResponseDone, PotentialDataLoss, ExcessWrite
from twisted.web._newclient import TransportProxyProducer, LengthEnforcingConsumer, makeStatefulDispatcher
from twisted.web.http_headers import Headers
from twisted.web.http import _DataLoss


class ArbitraryException(Exception):
    """
    A unique, arbitrary exception type which L{twisted.web._newclient} knows
    nothing about.
    """


class AnotherArbitraryException(Exception):
    """
    Similar to L{ArbitraryException} but with a different identity.
    """


# A re-usable Headers instance for tests which don't really care what headers
# they're sending.
_boringHeaders = Headers({'host': ['example.com']})


def assertWrapperExceptionTypes(self, deferred, mainType, reasonTypes):
    """
    Assert that the given L{Deferred} fails with the exception given by
    C{mainType} and that the exceptions wrapped by the instance of C{mainType}
    it fails with match the list of exception types given by C{reasonTypes}.

    This is a helper for testing failures of exceptions which subclass
    L{_newclient._WrapperException}.

    @param self: A L{TestCase} instance which will be used to make the
        assertions.

    @param deferred: The L{Deferred} which is expected to fail with
        C{mainType}.

    @param mainType: A L{_newclient._WrapperException} subclass which will be
        trapped on C{deferred}.

    @param reasonTypes: A sequence of exception types which will be trapped on
        the resulting L{mainType} exception instance's C{reasons} sequence.

    @return: A L{Deferred} which fires with the C{mainType} instance
        C{deferred} fails with, or which fails somehow.
    """
    def cbFailed(err):
        for reason, type in zip(err.reasons, reasonTypes):
            reason.trap(type)
        self.assertEqual(len(err.reasons), len(reasonTypes),
                         f"len({err.reasons}) != len({reasonTypes})")
        return err
    d = self.assertFailure(deferred, mainType)
    d.addCallback(cbFailed)
    return d


class MakeStatefulDispatcherTests(TestCase):
    """
    Tests for L{makeStatefulDispatcher}.
    """
    def test_functionCalledByState(self):
        """
        A method defined with L{makeStatefulDispatcher} invokes a second
        method based on the current state of the object.
        """
        class Foo:
            _state = 'A'

            def bar(self):
                pass
            bar = makeStatefulDispatcher('quux', bar)

            def _quux_A(self):
                return 'a'

            def _quux_B(self):
                return 'b'

        stateful = Foo()
        self.assertEqual(stateful.bar(), 'a')
        stateful._state = 'B'
        self.assertEqual(stateful.bar(), 'b')
        stateful._state = 'C'
        with self.assertRaises(RuntimeError):
            stateful.bar()


class HTTPParserTests(unittest.TestCase):
    """
    Base test class for L{HTTPParser} which is responsible for the bulk of
    the task of parsing HTTP bytes.
    """
    sep = None

    def test_statusCallback(self):
        """
        L{HTTPParser} calls its C{statusReceived} method when it receives a
        status line.
        """
        status = []
        protocol = HTTPParser()
        protocol.statusReceived = status.append
        protocol.makeConnection(StringTransport())
        self.assertEqual(protocol.state, STATUS)
        protocol.dataReceived(f'HTTP/1.1 200 OK{self.sep}')
        self.assertEqual(status
