# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Dict client protocol implementation.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import twisted.internet
import twisted.internet.defer
import twisted.internet.protocol
import twisted.python.log
from twisted.protocols import basic


class InvalidResponse(Exception):
    """Exception raised for invalid response from the server."""


def parse_param(line: str) -> Tuple[Optional[str], str]:
    """Parse a parameter from the line.

    Args:
        line (str): The line to parse.

    Returns:
        Tuple[Optional[str], str]: A tuple containing the parameter value and the remaining line.
    """
    if not line:
        return None, ""
    elif line[0] != '"':  # atom
        mode = 1
    else:  # dqstring
        mode = 2
    res = ""
    i = 0
    for c in line:
        i += 1
        if c == '"':
            if mode == 2:
                if i < len(line) and line[i] == '"':
                    res += c
                    i += 1
                else:
                    return res, line[i:]
        elif c == '\\':
            if i < len(line) - 1:
                res += line[i - 1 : i] + line[i + 1 : i + 2]
                i += 1
            else:
                return None, line
        elif c == ' ':
            if mode == 1:
                return res, line[i:]
        res += c
    return res, ""


def make_atom(line: str) -> str:
    """Create an atom from the line.

    Args:
        line (str): The line to create an atom from.

    Returns:
        str: The atom.
    """
    # FIXME: proper quoting
    return re.sub(r"[^\w]", "", line)


def make_word(s: str) -> str:
    """Create a word from the string `s`.

    Args:
        s (str): The string to create a word from.

    Returns:
        str: The word.
    """
    mustquote = set(range(33)) | {34, 39, 92}
    result = []
    for c in s:
        if ord(c) in mustquote:
            result.append("\\")
        result.append(c)
    s = "".join(result)
    return s


def parse_text(line: str) -> Optional[str]:
    """Parse text from the line.

    Args:
        line (str): The line to parse.

    Returns:
        Optional[str]: The parsed text or None if the line is empty.
    """
    if not line:
        return None
    elif line[0:2] == "..":
        return line[2:]
    return line


class Definition:
    """A word definition."""

    def __init__(
        self, name: str, db: str, dbdesc: str, text: List[str]
    ) -> None:
        """Initialize the definition.

        Args:
            name (str): The name of the definition.
            db (str): The database of the definition.
            dbdesc (str): The description of the database.
            text (List[str]): The text of the definition.
        """
        self.name = name
        self.db = db
        self.dbdesc = dbdesc
        self.text = text


class DictClient(basic.LineReceiver):
    """dict (RFC2229) client."""

    data = None  # multiline data
    MAX_LENGTH = 1024
    state = None
    mode = None
    result = None
    factory = None

    def __init__(self) -> None:
        """Initialize the client."""
        self.data = None
        self.result = None

    def connectionMade(self) -> None:
        """Called when the connection is made."""
        self.state = "conn"
        self.mode = "command"

    def sendLine(self, line: str) -> None:
        """Send a line.

        Args:
            line (str): The line to send.
        """
        if len(line) > self.MAX_LENGTH - 2:
            raise ValueError("DictClient tried to send a too long line")
        basic.LineReceiver.sendLine(self, line)

    def lineReceived(self, line: str) -> None:
        """Called when a line is received.

        Args:
            line (str): The line received.
        """
        try:
            line = line.decode("UTF-8")
        except UnicodeError:  # garbage received, skip
            return
        if self.mode == "text":  # we are receiving textual data
            code = "text"
        else:
            if len(line) < 4:
                twisted.python.log.msg(
                    "DictClient got invalid line from server -- %s" % line
                )
                self.protocolError("Invalid line from server")
                self.transport.loseConnection()
                return
            code = int(line[:3])
            line = line[4:]
        method = getattr(
            self, "dictCode_%s_%s" % (code, self.state), self.dictCode_default
        )
        method(line)

    def dictCode_default(self, line: str) -> None:
        """Unkown message
