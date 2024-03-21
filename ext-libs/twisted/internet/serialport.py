# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
Serial Port Protocol
"""

import os
import sys
import serial

__all__ = [
    "serial",
    "PARITY_ODD",
    "PARITY_EVEN",
    "PARITY_NONE",
    "STOPBITS_TWO",
    "STOPBITS_ONE",
    "FIVEBITS",
    "EIGHTBITS",
    "SEVENBITS",
    "SIXBITS",
    "SerialPort",
]


class BaseSerialPort:
    """
    Base class for Windows and POSIX serial ports.

    @ivar _serialFactory: a pyserial `serial.Serial` factory, used to create
        the instance stored in `self._serial`. Overrideable to enable easier
        testing.

    @ivar _serial: a pyserial `serial.Serial` instance used to manage the
        options on the serial port.
    """

    _serialFactory = serial.Serial

    def __init_subclass__(cls):
        if os.name == "posix":
            cls._serialFactory = serial.Serial
        elif sys.platform == "win32":
            from twisted.internet._win32serialport import Serial

            cls._serialFactory = Serial

