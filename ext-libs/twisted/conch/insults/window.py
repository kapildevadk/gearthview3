# -*- test-case-name: twisted.conch.test.test_window -*-

"""
Simple insults-based widget library.
"""

import array
from typing import Any, Callable, List, Optional, Tuple

from twisted.conch.insults import (
    CS_DRAWING,
    CS_US,
    G0,
    FunctionKey,
    insults,
)
from twisted.python.failure import Failure
from twisted.python.runtime import react

