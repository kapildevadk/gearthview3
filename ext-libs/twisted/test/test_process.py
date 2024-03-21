import os
import sys
import signal
import gzip
import errno
import gc
import stat
import operator
import shutil
import tempfile
import zope.interface.verify
from zope.interface import Interface, implementer
from twisted.python.log import msg
from twisted.internet import reactor, protocol, defer, interfaces, error, utils
from twisted.trial import unittest
from twisted.python.failure import Failure
from twisted.python.runtime import platform
from twisted.python.util import sibpath
from twisted.python.test import mock_win32process
from twisted.internet.process import Process, ProcessProtocol
from twisted.internet.stdio import Accumulator
from twisted.internet.defer import gatherResults
from typing import Any, Callable, Dict, List, NoReturn, Optional, Text, Type, Union
from unittest.mock import Mock, patch


class IProcessProtocol(Interface):
    def outReceived(self, data: bytes) -> None:
        ...

    def errReceived(self, data: bytes) -> None:
        ...

    def inConnectionLost(self) -> None:
        ...

    def outConnectionLost(self) -> None:
        ...

    def errConnectionLost(self) -> None:
        ...

    def processEnded(self, reason: Any) -> None:
        ...


@implementer(IProcessProtocol)
class StubProcessProtocol(ProcessProtocol):
    def outReceived(self, data: bytes) -> None:
        raise NotImplementedError()

    def errReceived(self, data: bytes) -> None:
        raise NotImplementedError()

    def inConnectionLost(self) -> None:
        raise NotImplementedError()

    def outConnectionLost(self) -> None:
        raise NotImplementedError()

    def errConnectionLost(self) -> None:
        raise NotImplementedError()


class ProcessProtocolTests(unittest.TestCase):
    def test_interface(self) -> None:
        zope.interface.verify.verifyObject(IProcessProtocol, protocol.ProcessProtocol)

    def test_outReceived(self) -> None:
        received: List[bytes] = []
        class OutProtocol(StubProcessProtocol):
            def outReceived(self, data: bytes) -> None:
                received.append(data)

        bytes_: bytes = b"bytes"
        p: OutProtocol = OutProtocol()
        p.childDataReceived(1, bytes_)
        self.assertEqual(received, [bytes_])

    def test_errReceived(self) -> None:
        received: List[bytes] = []
        class ErrProtocol(StubProcessProtocol):
            def errReceived(self, data: bytes) -> None:
                received.append(data)

        bytes_: bytes = b"bytes"
        p: ErrProtocol = ErrProtocol()
        p.childDataReceived(2, bytes_)
        self.assertEqual(received, [bytes_])

    def test_inConnectionLost(self) -> None:
        lost: List[None] = []
        class InLostProtocol(StubProcessProtocol):
            def inConnectionLost(self) -> None:
                lost.append(None)

        p: InLostProtocol = InLostProtocol()
        p.childConnectionLost(0)
        self.assertEqual(lost, [None])

    def test_outConnectionLost(self) -> None:
        lost: List[None] = []
        class OutLostProtocol(StubProcessProtocol):
            def outConnectionLost(self) -> None:
                lost.append(None)

        p: OutLostProtocol = OutLostProtocol()
        p.childConnectionLost(1)
        self.assertEqual(lost, [None])

    def test_errConnectionLost(self) -> None:
        lost: List[None] = []
        class ErrLostProtocol(StubProcessProtocol):
            def errConnectionLost(self) -> None:
                lost.append(None)

        p: ErrLostProtocol = ErrLostProtocol()
        p.childConnectionLost(2)
        self.assertEqual(lost, [None])


class TrivialProcessProtocol(ProcessProtocol):
    def __init__(self, d: defer.Deferred) -> None:
        self.deferred = d
        self.outData: List[bytes] = []
        self.errData: List[bytes] = []

    def processEnded(self, reason: Any) -> None:
        self.reason = reason
        self.deferred.callback(None)

    def outReceived(self, data: bytes) -> None:
        self.outData.append(data)

    def errReceived(self, data: bytes) -> None:
        self.errData.append(data)


class TestProcessProtocol(ProcessProtocol):
    def connectionMade(self) -> None:
        self.stages: List[int] = [1]
        self.data: str = ''
        self.err: str = ''
        self.transport.write(b"abcd")

    def childDataReceived(self, childFD: int, data: bytes) -> None:
        super().childDataReceived(childFD, data)
        if childFD == 1:
            self.data += data.decode()
        elif childFD == 2:
            self.err += data.decode()

    def childConnectionLost(self, childFD: int) -> None
