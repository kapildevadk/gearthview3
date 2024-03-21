# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module contains interfaces defined for the L{twisted.conch} package.
"""

from zope.interface import Interface, Attribute
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

class IConchUser(Interface):
    """
    A user who has been authenticated to Cred through Conch.  This is
    the interface between the SSH connection and the user.
    """

    conn: 'SSHConnection'

    def lookupChannel(self, channelType: str, windowSize: int, maxPacket: int, data: str) -> 'SSHChannel':
        ...

    def lookupSubsystem(self, subsystem: str, data: str) -> 'Protocol':
        ...

    def gotGlobalRequest(self, requestType: str, data: str) -> None:
        ...

class ISession(Interface):

    def getPty(self, term: str, windowSize: Tuple[int, int], modes: Dict[str, Any]) -> None:
        ...

    def openShell(self, proto: 'ProcessProtocol') -> None:
        ...

    def execCommand(self, proto: 'ProcessProtocol', command: str) -> None:
        ...

    def windowChanged(self, newWindowSize: Tuple[int, int]) -> None:
        ...

    def eofReceived(self) -> None:
        ...

    def closed(self) -> None:
        ...

class ISFTPServer(Interface):
    """
    The only attribute of this class is "avatar".  It is the avatar
    returned by the Realm that we are authenticated with, and
    represents the logged-in user.  Each method should check to verify

