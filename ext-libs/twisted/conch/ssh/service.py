# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
The parent class for all the SSH services.  Currently implemented services
are ssh-userauth and ssh-connection.

Maintainer: Paul Swartz
"""

import typing

from twisted.python import log
from twisted.python.util import getAttribute

class SSHService(log.Logger):
    """
    The parent class for all the SSH services.
    """

    name: str
    transport: typing.Any

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def getProtocolMessageName(cls, message_num: int) -> str:
        """
        Get the protocol message name for the given message number.
        """
        if message_num in cls.protocolMessages:
            return cls.protocolMessages[message_num]
        return f"Unknown-{message_num}"

    def serviceStarted(self) -> None:
        """
        Called when the service is active on the transport.
        """
        pass

    def serviceStopped(self) -> None:
        """
        Called when the service is stopped, either by the connection ending
        or by another service being started
        """
        pass

    def logPrefix(self) -> str:
        return f"SSHService {self.name} on {self.transport.transport.logPrefix()}"

    def packetReceived(self, message_num: int, packet: bytes) -> None:
        """
        Called when we receive a packet on the transport
        """
        message_type = self.getProtocolMessageName(message_num)
        f = getAttribute(f"ssh_{message_type[4:]}", self, None)
        if f is not None:
            return f
