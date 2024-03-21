# -*- test-case-name: twisted.test.test_logfile -*-

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
A rotating, browsable log file.
"""

# System Imports
import os
import glob
import time
import stat
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import threadable


class BaseLogFile:
    """
    The base class for a log file that can be rotated.
    """

    synchronized = ["write", "rotate"]

    def __init__(
        self,
        name: str,
        directory: str,
        default_mode: Optional[int] = None,
    ) -> None:
        """
        Create a log file.

        :param name: name of the file
        :param directory: directory holding the file
        :param default_mode: permissions used to create the file. Default to
            current permissions of the file if the file exists.
        """
        self.directory = directory
        self.name = name
        self.path = os.path.join(directory, name)
        if default_mode is None and os.path.exists(self.path):
            st = os.stat(self.path)
            self.default_mode = stat.S_IMODE(st[stat.ST_MODE])
        else:
            self.default_mode = default_mode
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self._open_file()

    @classmethod
    def from_full_path(
        cls, filename: str, *args, **kwargs
    ) -> "BaseLogFile":
        """
        Construct a log file from a full file path.
        """
        log_path = os.path.abspath(filename)
        return cls(os.path.basename(log_path), os.path.dirname(log_path), *args, **kwargs)

    def should_rotate(self) -> bool:
        """
        Override with a method to that returns true if the log
        should be rotated.
        """
        raise NotImplementedError

    def _open_file(self) -> None:
        """
        Open the log file.
        """
        self.closed = False
        if os.path.exists(self.path):
            self._file = open(self.path, "r+", 1)
            self._file.seek(0, 2)
        else:
            if self.default_mode is not None:
                # Set the lowest permissions
                old_umask = os.umask(0777)
                try:
                    self._file = open(self.path, "w+", 1)
                finally:
                    os.umask(old_umask)
            else:
                self._file = open(self.path, "w+", 1)
        if self.default_mode is not None:
            try:
                os.chmod(self.path, self.default_mode)
            except OSError:
                # Probably /dev/null or something?
                pass

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        del state["_file"]
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__ = state
        self._open_file()

    def write(self, data: str) -> None:
        """
        Write some data to the file.
        """
        if self.should_rotate():
            self.flush()
            self.rotate()
        self._file.write(data)

    def flush(self) -> None:
        """
        Flush the file.
        """
        self._file.flush()

    def close(self) -> None:
        """
        Close the file.

        The file cannot be used once it has been closed.
        """
        self.closed = True
        self._file.close()
        self._file = None

    def reopen(self) -> None:
        """
        Reopen the log file. This is mainly useful if you use an external log
        rotation tool, which moves under your feet.

        Note that on Windows you probably need a specific API to rename the
        file, as it's not supported to simply use os.rename, for example.
        """
        self.close()
        self._open_file()

    def get_current_log(self) -> "LogReader":
        """
        Return a LogReader for the current log file.
        """
        return LogReader(self.path)


class LogFile(BaseLogFile):
    """
    A log file that can be rotated.

    A rotate_length of None disables automatic log rotation.
    """

    def __init__(
        self,
        name: str,
        directory: str,
        rotate_length: Optional[int] = 1000000,
        default_mode: Optional[int] = None,

