# -*- test-case-name: twisted.test.test_compat -*-
#
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
Compatibility module to provide backwards compatibility for useful Python
features.

This is mainly for use of internal Twisted code. We encourage you to use
the latest version of Python directly from your code, if possible.

@var unicode: The type of Unicode strings, C{unicode} on Python 2 and C{str}
    on Python 3.

@var NativeStringIO: An in-memory file-like object that operates on the native
    string type (bytes in Python 2, unicode in Python 3).
"""

import sys
from functools import reduce, lru_cache
from io import StringIO, BytesIO
import socket
import struct
import string
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

if sys.version_info < (3, 0):
    _PY3 = False
else:
    _PY3 = True


def inet_pton(af: int, addr: str) -> bytes:
    if af == socket.AF_INET:
        return socket.inet_aton(addr)
    elif af == getattr(socket, "AF_INET6", "AF_INET6"):
        if [x for x in addr if x not in string.hexdigits + ":."]:
            raise ValueError("Illegal characters: {}".format("".join(x)))

        parts = addr.split(":")
        elided = parts.count("")
        ipv4_component = "." in parts[-1]

        if len(parts) > (8 - ipv4_component) or elided > 3:
            raise ValueError("Syntactically invalid address")

        if elided == 3:
            return b"\x00" * 16

        if elided:
            zeros = ["0"] * (8 - len(parts) - ipv4_component + elided)

            if addr.startswith("::"):
                parts[:2] = zeros
            elif addr.endswith("::"):
                parts[-2:] = zeros
            else:
                idx = parts.index("")
                parts[idx : idx + 1] = zeros

            if len(parts) != 8 - ipv4_component:
                raise ValueError("Syntactically invalid address")
        else:
            if len(parts) != (8 - ipv4_component):
                raise ValueError("Syntactically invalid address")

        if ipv4_component:
            if parts[-1].count(".") != 3:
                raise ValueError("Syntactically invalid address")
            rawipv4 = socket.inet_aton(parts[-1])
            unpackedipv4 = struct.unpack("!HH", rawipv4)
            parts[-1:] = [hex(x)[2:] for x in unpackedipv4]

        parts = [int(x, 16) for x in parts]
        return struct.pack("!8H", *parts)
    else:
        raise socket.error(97, "Address family not supported by protocol")


@lru_cache()
def inet_ntop(af: int, addr: bytes) -> str:
    if af == socket.AF_INET:
        return socket.inet_ntoa(addr)
    elif af == socket.AF_INET6:
        if len(addr) != 16:
            raise ValueError("address length incorrect")
        parts = struct.unpack("!8H", addr)
        cur_base = best_base = None
        for i in range(8):
            if not parts[i]:
                if cur_base is None:
                    cur_base = i
                    cur_len = 0
                cur_len += 1
            else:
                if cur_base is not None:
                    if best_base is None or cur_len > best_len:
                        best_base = cur_base
                        best_len = cur_len
                    cur_base = None
        if cur_base is not None and (
            best_base is None or cur_len > best_len
        ):
            best_base = cur_base
            best_len = cur_len
        parts = [hex(x)[2:] for x in parts]
        if best_base is not None:
            parts[best_base : best_base + best_len] = [""]
        if parts[0] == "":
            parts.insert(0, "")
        if parts[-1] == "":
            parts.insert(len(parts) - 1, "")
        return ":".join(parts)
    else:
        raise socket.error(97, "Address family not supported by protocol")


try:
    socket.AF_INET6
except AttributeError:
    socket.AF_INET6 = "AF_INET6"

try:
    socket.inet_pton(socket.AF_INET6, "::")
except (AttributeError, NameError, socket.error):
    socket.inet_pton = inet_pton
    socket.inet_ntop = inet_ntop


NativeStringIO = StringIO if _PY3 else BytesIO


def execfile(filename: str, globals: Dict[str, Any], locals: Optional[Dict[str, Any]] = None) -> None:
    """
    Execute a Python script in the given namespaces.

    Similar
