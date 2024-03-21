# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.internet._baseprocess} which implements process-related
functionality that is useful in all platforms supporting L{IReactorProcess}.
"""

import unittest
from unittest.mock import Mock, patch
import warnings
from twisted.python.deprecate import getWarningMethod, setWarningMethod
from twisted.trial.unittest import TestCase
from twisted.internet._baseprocess import BaseProcess


class BaseProcessTests(TestCase):
    """
    Tests for L{BaseProcess}, a parent class for other classes which represent
    processes which implements functionality common to many different process
    implementations.
    """

    def test_callProcessExited(self):
        """
        L{BaseProcess._callProcessExited} calls the C{processExited} method of
        its C{proto} attribute and passes it a L{Failure} wrapping the given
        exception.
        """
        proto = Mock()
        process = BaseProcess(proto)
        reason = RuntimeError("fake reason")
        process._callProcessExited(reason)
        proto.processExited.assert_called_once_with(unittest.expectedFailure(reason))

    def test_callProcessExitedMissing(self):
        """
        L{BaseProcess._callProcessExited} emits a L{DeprecationWarning} if the
        object referred to by its C{proto} attribute has no C{processExited}
        method.
        """
        proto = Mock()
        process = BaseProcess(proto)

        with patch('twisted.python.deprecate.getWarningMethod') as getWarningMethodMock:
            getWarningMethodMock.return_value = lambda message: None
            with self.assertWarns(DeprecationWarning):
                process._callProcessExited(RuntimeError("fake reason"))

            getWarningMethodMock.assert_called_once_with()
            getWarningMethodMock.return_value.assert_called_once_with(
                "Since Twisted 8.2, IProcessProtocol.processExited is required.  "
                "%s.%s must implement it." % (
                    proto.__module__, proto.__name__))
