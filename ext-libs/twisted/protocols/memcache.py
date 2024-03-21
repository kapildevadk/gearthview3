# -*- test-case-name: twisted.test.test_memcache -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Memcache client protocol. Memcached is a caching server, storing data in the
form of pairs key/value, and memcache is the protocol to talk with it.
"""

import collections
import sys

import twisted.protocols.basic
import twisted.protocols.policies
import twisted.internet.defer
import twisted.python.log

