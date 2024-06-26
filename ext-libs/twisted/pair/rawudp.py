# -*- test-case-name: twisted.pair.test.test_rawudp -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""Implementation of raw packet interfaces for UDP"""

import struct
from collections import defaultdict
from twisted.internet import protocol
from twisted.pair import raw
from zope.interface import implements

class UDPHeader:
    """UDP header class to extract source, destination, length, and checksum"""

    def __init__(self, data):
        (self.source, self.dest, self.len, self.check) = struct.unpack("!HHHH", data[:8])

class RawUDPProtocol(protocol.AbstractDatagramProtocol):
    """UDP protocol class implementing the IRawDatagramProtocol interface"""

    implements(raw.IRawDatagramProtocol)

    def __init__(self):
        self.udpProtos = defaultdict(list)

    def addProto(self, num, proto):
        """Add a new protocol to the UDP protocol list"""
        if not isinstance(proto, protocol.DatagramProtocol):
            raise TypeError('Added protocol must be an instance of DatagramProtocol')
        if num < 0:
            raise TypeError('Added protocol number must be positive or zero')
        if num >= 2**16:
            raise TypeError('Added protocol number must fit in 16 bits')
        self.udpProtos[num].append(proto)

    def datagramReceived(self, data, source, dest, protocol, version, ihl, tos, tot_len, fragment_id, fragment_offset, dont_fragment, more_fragments, ttl):
        """Handle incoming UDP datagrams and pass them to the appropriate protocol"""
        header = UDPHeader(data)
        for proto in self.udpProtos.get(header.dest, ()):
            proto.datagramReceived(data[8:], (source, header.source))
