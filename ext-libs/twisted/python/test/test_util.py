# -*- test-case-name: twisted.python.test.test_util
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.util}.
"""

import os.path
import sys
import shutil
import errno
import warnings
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

try:
    import pwd
    import grp
except ImportError:
    pwd = grp = None

import unittest
from unittest.util import suppress
from unittest.warnings import catch_warnings
from unittest.warnings import filterwarnings
from unittest.warnings import simplefilter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from twisted.internet import interfaces
    from twisted.python.versions import Version

    from twisted.python.compat import _PY3
else:
    _PY3 = getattr(sys, "version_info", (3,)).major == 3

