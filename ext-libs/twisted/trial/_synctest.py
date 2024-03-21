# -*- test-case-name: twisted.trial.test -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Things likely to be used by writers of unit tests.

Maintainer: Jonathan Lange
"""

from __future__ import division, absolute_import

import inspect
import os
import sys
import tempfile
import warnings
from typing import (Any, Callable, Dict, Iterable, List, List, NoReturn,
                    Optional, Tuple, Type, TypeVar, Union)
from typing import overload
from typing_extensions import Final
from unittest import TestCase, TextTestResult, defaultTestResult
from unittest.mock import patch
from twisted.python import failure, log, monkey
from twisted.python.util import runWithWarningsSuppressed
from twisted.python.deprecate import (
    getDeprecationWarningString, warnAboutFunction)
from twisted.trial import itrial, util
from twisted.trial.itrial import IReporter
from contextlib import (
    suppress,
    ExitStack,
)
from contextvars import ContextVar

T = TypeVar('T')


class FailTest(AssertionError):
    """Raised to indicate the current test has failed to pass."""


class Todo:
    """
    Internal object used to mark a L{TestCase} as 'todo'. Tests marked 'todo'
    are reported differently in Trial L{TestResult}s. If todo'd tests fail,
    they do not fail the suite and the errors are reported in a separate
    category. If todo'd tests succeed, Trial L{TestResult}s will report an
    unexpected success.
    """

    def __init__(self, reason: str, errors: Optional[Iterable[Type[Exception]]] = None):
        """
        @param reason: A string explaining why the test is marked 'todo'

        @param errors: An iterable of exception types that the test is
        expected to raise. If one of these errors is raised by the test, it
        will be trapped. Raising any other kind of error will fail the test.
        If C{None} is passed, then all errors will be trapped.
        """
        self.reason = reason
        self.errors = errors

    def __repr__(self):
        return "<Todo reason=%r errors=%r>" % (self.reason, self.errors)

    def expected(self, failure: failure.Failure) -> bool:
        """
        @param failure: A L{twisted.python.failure.Failure}.

        @return: C{True} if C{failure} is expected, C{False} otherwise.
        """
        if self.errors is None:
            return True
        for error in self.errors:
            if failure.check(error):
                return True
        return False


def makeTodo(value: Union[str, Tuple[Type[Exception], str]]) -> Todo:
    """
    Return a L{Todo} object built from C{value}.

    If C{value} is a string, return a Todo that expects any exception with
    C{value} as a reason. If C{value} is a tuple, the second element is used
    as the reason and the first element as the excepted error(s).

    @param value: A string or a tuple of C{(errors, reason)}, where C{errors}
    is either a single exception class or an iterable of exception classes.

    @return: A L{Todo} object.
    """
    if isinstance(value, str):
        return Todo(reason=value)
    if isinstance(value, tuple):
        errors, reason = value
        try:
            errors = list(errors)
        except TypeError:
            errors = [errors]
        return Todo(reason=reason
