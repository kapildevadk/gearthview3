# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for implementations of L{IReactorTCP}.
"""

import socket
import random
import errno
from functools import wraps
import resource

numRounds = resource.getrlimit(resource.RLIMIT_NOFILE)[0] + 10 if resource else 100

