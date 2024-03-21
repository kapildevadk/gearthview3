# -*- test-case-name: twisted.conch.test.test_telnet -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Telnet protocol implementation.

@author: Jean-Paul Calderone
"""

import struct
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from zope.interface import implementer

from twisted.internet import protocol, defer
from twisted.python import log

MODE = 1
EDIT = 1
TRAPSIG = 2
MODE_ACK = 4
SOFT_TAB = 8
LIT_ECHO = 16

NULL = chr(0)
BEL = chr(7)
BS = chr(8)
HT = chr(9)
LF = chr(10)
VT = chr(11)
FF = chr(12)
CR = chr(13)

ECHO = chr(1)
SGA = chr(3)
NAWS = chr(31)
LINEMODE = chr(34)

IAC = chr(255)

class ITelnetProtocol:
    def unhandledCommand(self, command: str, argument: Optional[str]) -> None:
        """A command was received but not understood.

        @param command: the command received.
        @type command: C{str}, a single character.
        @param argument: the argument to the received command.
        @type argument: C{str}, a single character, or None if the command that
            was unhandled does not provide an argument.
        """

    def unhandledSubnegotiation(self, command: str, bytes: List[str]) -> None:
        """A subnegotiation command was received but not understood.

        @param command: the command being subnegotiated. That is, the first
            byte after the SB command.
        @type command: C{str}, a single character.
        @param bytes: all other bytes of the subneogation. That is, all but the
            first bytes between SB and SE, with IAC un-escaping applied.
        @type bytes: C{list} of C{str}, each a single character
        """

    def enableLocal(self, option: str) -> bool:
        """Enable the given option locally.

        This should enable the given option on this side of the
        telnet connection and return True.  If False is returned,

