# -*- test-case-name: twisted.test.test_defer,twisted.test.test_defgen,twisted.internet.test.test_inlinecb -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Support for results that aren't immediately available.
"""

from __future__ import division, absolute_import

import sys
import traceback
import types
import warnings
from sys import exc_info
from functools import wraps

# Twisted imports
from twisted.python.compat import _PY3, comparable, cmp
from twisted.python import log, failure
from twisted.python.util import Failure

