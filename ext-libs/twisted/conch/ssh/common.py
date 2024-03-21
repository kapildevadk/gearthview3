# -*- test-case-name: twisted.conch.test.test_ssh -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
Common functions for the SSH classes.

Maintainer: Paul Swartz
"""

import struct
import warnings
import random
import builtins

try:
    from Crypto.Util import number
except ImportError:
    warnings.warn("PyCrypto not installed, but continuing anyways!", RuntimeWarning)


def NS(t: str) -> bytes:
    """
    net string
    """
    return struct.pack('!L', len(t)) + t

def getNS(s: bytes, count: int = 1) -> tuple:
    """
    get net string
    """
    ns = []
    c = 0
    for i in range(count):
        l, = struct.unpack('!L', s[c:c + 4])
        ns.append(s[c + 4:4 + l + c])
        c += 4 + l
    return tuple(ns) + (s[c:],)

def MP(number: int) -> bytes:
    if number == 0:
        return b'\000' * 4
    assert number > 0
    bn = number.to_bytes((number.bit_length() + 7) // 8, 'big')
    if bn[0] & 128:
        bn = b'\000' + bn
    return struct.pack('>L', len(bn)) + bn

def getMP(data: bytes, count: int = 1) -> tuple:
    """
    Get multiple precision integer out of the string.  A multiple precision
    integer is stored as a 4-byte length followed by length bytes of the

