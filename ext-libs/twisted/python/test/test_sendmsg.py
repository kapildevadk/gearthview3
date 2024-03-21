# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.sendmsg}.
"""

import sys
import errno
from socket import SOL_SOCKET, AF_INET, AF_INET6, socket, error, MSG_DONTWAIT
from struct import pack
from os import devnull, pipe, read, close, environ, fdopen
from typing import Any, Callable, Union, List, Tuple
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.error import ProcessDone
from twisted.internet.interfaces import IProcessProtocol
from twisted.internet.stdio import StandardIO
from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.python.runtime import platform
from twisted.python.util import runWithWarningsSuppressed
from twisted.internet.protocol import ProcessProtocol
from twisted.python.failure import Failure

if platform.isLinux():
    dontWaitSkip = None
else:
    # It would be nice to be able to test flags on more platforms, but finding a
    # flag that works *at all* is somewhat challenging.
    dontWaitSkip = "MSG_DONTWAIT is only known to work as intended on Linux"

try:
    from twisted.python.sendmsg import SCM_RIGHTS, send1msg, recv1msg, getsockfam
except ImportError:
    importSkip = "Cannot import twisted.python.sendmsg"
else:
    importSkip = None


class ExitedWithStderr(Exception):
    """
    A process exited with some stderr.
    """

    def __init__(self, errors: str, output: str):
        self.errors = errors
        self.output = output

    def __str__(self):
        """
        Dump the errors in a pretty way in the event of a subprocess traceback.
        """
        return '\n'.join([''] + list(self.args))


class StartStopProcessProtocol(ProcessProtocol, StandardIO):
    """
    An L{IProcessProtocol} with a Deferred for events where the subprocess
    starts and stops.

    @ivar started: A L{Deferred} which fires with this protocol's
        L{IProcessTransport} provider when it is connected to one.

    @ivar stopped: A L{Deferred} which fires with the process output or a
        failure if the process produces output on standard error.

    @ivar output: A C{str} used to accumulate standard output.

    @ivar errors: A C{str} used to accumulate standard error.
    """
    def __init__(self):
        self.started = Deferred()
        self.stopped = Deferred()
        self.output = ''
        self.errors = ''

    def connectionMade(self, transport: IProcessTransport):
        """
        Called when the transport is connected.

        @param transport: The transport connected to the process.
        @type transport: L{IProcessTransport}
        """
        self.transport = transport
        self.started.callback(transport)

    def outReceived(self, data: bytes):
        """
        Called when data is received on stdout.

        @param data: The data received on stdout.
        @type data: C{bytes}
        """
        self.output += data.decode()

    def errReceived(self, data: bytes):
        """
        Called when data is received on stderr.

        @param data: The data received on stderr.
        @type data: C{bytes}
       
