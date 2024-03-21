# -*- test-case-name: twisted.test.test_paths -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Object-oriented filesystem path representation.
"""

from __future__ import division, absolute_import

import os
import errno
import base64
from hashlib import sha1
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

from os.path import (isabs, exists, normpath, abspath, splitext, basename,
                     dirname, join as joinpath)
from os import sep as slash
from os import listdir, utime, stat
from stat import (S_ISREG, S_ISDIR, S_IMODE, S_ISBLK, S_ISSOCK, S_IRUSR,
                  S_IWUSR, S_IXUSR, S_IRGRP, S_IWGRP, S_IXGRP, S_IROTH,
                  S_IWOTH, S_IXOTH)

from zope.interface import Interface, Attribute, implementer
from typing import TypeVar, Generic

T = TypeVar('T')


class IFilePath(Interface):
    """
    File path object.

    A file path represents a location for a file-like-object and can be
    organized into a hierarchy; a file path can have children which are
    themselves file paths.

    A file path has a name which unique identifies it in the context of its
    parent (if it
