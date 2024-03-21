# -*- test-case-name: twisted.conch.test.test_conch -*-
from interfaces import IConchUser
from error import ConchError
from ssh.connection import OPEN_UNKNOWN_CHANNEL_TYPE
from twisted.python import log
from zope import interface
from typing import Any, Dict, Optional

class ConchUser:
    """Implements the IConchUser interface for Twisted Conch SSH connections."""

    interface.implements(IConchUser)

    def __init__(self):
        self.channel_lookup: Dict[str, type] = {}
        self.subsystem_lookup: Dict[str, type] = {}

    def lookup_channel(self, channel_type: str, window_size: int, max_packet: int, data: Any) -> Any:
        """Look up and instantiate a channel class based on the given channel type."""
        ChannelClass = self.channel_lookup.get(channel_type, None)
        if not ChannelClass:
            raise ConchError(OPEN_UNKNOWN_CHANNEL_TYPE, f"Unknown channel type: {channel_type}")
        return ChannelClass(remote_window=window_size, remote_max_packet=max_packet, data=data, avatar=self)

    def lookup_subsystem(self, subsystem: str, data: Any) -> Optional[Any]:
        """Look up and instantiate a subsystem class based on the given subsystem name."""
        log.msg(f"Subsystem lookup: {self.subsystem_lookup}")
        SubsystemClass = self.subsystem_lookup.get(subsystem, None)
