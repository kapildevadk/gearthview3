# -*- test-case-name: twisted.test.test_process -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Cross-platform process-related functionality used by different
L{IReactorProcess} implementations.
"""

import typing
from twisted.python.reflect import qual
from twisted.python.deprecate import getWarningMethod
from twisted.python.failure import Failure
from twisted.python.log import err
from twisted.persisted.styles import Ephemeral

_missingProcessExited = ("Since Twisted 8.2, IProcessProtocol.processExited "
                         "is required.  %s must implement it.")

class BaseProcess(Ephemeral):
    """
    A base class for managing a process.
    """
    pid: typing.Optional[int] = None
    status: typing.Optional[int] = None
    lostProcess: int = 0
    proto: typing.Optional[typing.Any] = None

    def __init__(self, protocol: typing.Any):
        self.proto = protocol

    def _callProcessExited(self, reason: typing.Any):
        default = object()
        processExited = getattr(self.proto, 'processExited', default)
        if processExited is default:
            getWarningMethod()(
                _missingProcessExited % (qual(self.proto.__class__),),
                DeprecationWarning, stacklevel=0)
        else:
            processExited(Failure(reason))
            self.proto = None  # Set proto to None here to avoid multiple calls in maybeCallProcessEnded

    def processEnded(self, status: int):
        """
        This is called when the child terminates.
        """
        self.status = status
        self.lostProcess += 1
        self.pid = None
        self._callProcessExited(self._getReason(status))
        self.maybeCallProcessEnded()

    def maybeCallProcessEnded(self):
        """
        Call processEnded on protocol after final cleanup.
        """
        if self.proto is not None:
            reason = self._getReason(self.status)
            try:
                self.proto.processEnded(Failure(reason))
            except:
                err(None, "unexpected error in processEnded")
            finally:
                self.proto = None

    def __repr__(self) -> str:
        return f'<BaseProcess pid={self.pid} status={self.status} lostProcess={self.lostProcess} proto={self.proto}>'
