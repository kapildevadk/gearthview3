# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Errors to represent bad things happening in Conch.

Maintainer: Paul Swartz
"""

from twisted.cred.error import UnauthorizedLogin
from twisted.python.filepath import FilePath

class ConchError(Exception):
    def __init__(self, value, data=None):

