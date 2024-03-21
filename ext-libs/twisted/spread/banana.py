# -*- test-case-name: twisted.test.test_banana -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Banana -- s-exp based protocol.

Future Plans: This module is almost entirely stable.  The same caveat applies
to it as applies to L{twisted.spread.jelly}, however.  Read its future plans
for more details.

@author: Glyph Lefkowitz
"""

import struct
from typing import Any, Dict, List, Optional

from twisted.internet import protocol
from twisted.persisted import styles
from twisted.python import log

class BananaError(Exception):
    pass

def int2b128(integer: int, stream: str) -> None:
    if integer == 0:
        stream += chr(0)
        return
    assert integer > 0, "can only encode positive integers"
    while integer:
        stream += chr(integer & 0x7f)
        integer >>= 7

def b1282int(st: str) -> int:
    """
    Convert an integer represented as a base 128 string into an C{int} or
    C{long}.

    @param st: The integer encoded in a string.
    @type st: C{str}

    @return: The integer value extracted from the string.
    @rtype: C{int} or C{long}
    """
    e = 1
    i = 0
    for char in st:
        n = ord(char)
        i += (n * e)
        e <<= 7
    return i

# delimiter characters.
LIST     = chr(0x80)
INT      = chr(0x81)
STRING   = chr(0x82)
NEG      = chr(0x83)
FLOAT    = chr(0x84)
# "optional" -- these might be refused by a low-level implementation.
LONGINT  = chr(0x85)
LONGNEG  = chr(0x86)
# really optional; this is is part of the 'pb' vocabulary
VOCAB    = chr(0x87)

HIGH_BIT_SET = chr(0x80)

def setPrefixLimit(limit: int) -> None:
    """
    Set the limit on the prefix length for all Banana connections
    established after this call.

    The prefix length limit determines how many bytes of prefix a banana
    decoder will allow before rejecting a potential object as too large.

    @type limit: C{int}
    @param limit: The number of bytes of prefix for banana to allow when
    decoding.
    """
    global _PREFIX_LIMIT
    _PREFIX_LIMIT = limit
setPrefixLimit(64)

SIZE_LIMIT = 640 * 1024   # 640k is all you'll ever need :-)

class Banana(protocol.Protocol, styles.Ephemeral):
    """
    A protocol for communicating using s-expressions.

    @ivar knownDialects: A list of dialects that this protocol understands.
    @type knownDialects: C{list} of C{str}

    @ivar prefixLimit: The maximum length of the prefix allowed for decoding.
    @type prefixLimit: C{int}

    @ivar sizeLimit: The maximum size of a message allowed for decoding.
    @type sizeLimit: C{int}

    @ivar currentDialect: The current dialect being used for communication.
    @type currentDialect: C{str}

    @ivar listStack: A stack of lists being decoded.
    @type listStack: C{list} of C{tuple} of C{int} and C{list}

    @ivar buffer: A buffer of data waiting to be decoded.
    @type buffer: C{str}

    @ivar outgoingSymbols: A dictionary of outgoing symbols and their IDs.
    @type outgoingSymbols: C{dict} of C{str} and C{int}

    @ivar outgoingSymbolCount: The next available ID for an outgoing symbol.
    @type outgoingSymbolCount: C{int}

    @ivar isClient: Whether this protocol is a client or not.
    @type isClient: C{bool}

    @ivar incomingVocabulary: A dictionary of incoming symbol IDs and their names.
    @type incomingVocabulary: C{dict} of C{int} and C{str}
    """
    knownDialects = ["pb", "none"]

    prefixLimit: Optional[int] = None
    sizeLimit = SIZE_LIMIT

    def __init__(self, isClient: bool = True) -> None:
        self.listStack = []
        self.outgoingSymbols = copy.copy(self.outgoingVocabulary)
        self.outgoingSymbolCount = 0
        self.isClient = isClient

    def setPrefixLimit(self, limit: int) -> None:
        """
        Set the prefix limit for decoding done by this protocol instance.

        @see: L{setPrefixLimit}
        """
        self.prefixLimit = limit
        self._smallestLongInt = -2 ** (limit * 7) + 1
        self._smallestInt = -2 ** 31
        self._largestInt = 2 ** 31 - 1
        self._largestLongInt = 2 ** (limit * 7)
