# -*- test-case-name: twisted.python.test.test_hashlib -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
twisted.python.hashlib.py: A subset of the hashlib interface required by Twisted.
"""

import six.moves.hashlib as _hashlib

try:
    md5 = _hashlib.md5
    sha1 = _hashlib.sha1
except AttributeError:
    # Python 3.5+ has md5 and sha1 in hashlib, but Python 2 doesn't.
    # six.moves.hashlib provides a consistent interface for both versions.
    md5 = _hashlib.new('md5')
    sha1 = _hashlib.new('sha1')

__all__ = ["md5", "sha1"]
