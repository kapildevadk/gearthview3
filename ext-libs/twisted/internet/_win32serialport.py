# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Serial port support for Windows.

Requires PySerial and pywin32.
"""

import serial
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD
from serial import STOPBITS_ONE, STOPBITS_TWO
from serial import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
import win32file
import win32event
from typing import Any
from twisted.internet import abstract
from twisted.internet.interfaces import IFileDescriptor
from twisted.python.failure import Failure

# sibling imports
from serialport import BaseSerialPort

class SerialPort(BaseSerialPort, abstract.FileDescriptor):
    """A serial device, acting as a transport, that uses a win32 event."""

    connected = 1

    def __init__(
        self,
        protocol: Any,
        device_name_or_port_number: str,
        reactor,
        baudrate: int = 960
