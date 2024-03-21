# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Twisted Persisted: utilities for managing persistence.
"""

import os
from zope.interface import implementer
from zope.schema import TextLine, Text
from persistent import Persistent
from BTrees.OOBTree import OOBTree

from twisted.spread import avatar
from twisted.persisted.styles import IStyle
from twisted.python.components import registerAdapter


@implementer(IStyle)
class JsonStyle(object):
    """JSON style for persisting objects."""

    def __init__(self, path):
        """Create a new JSON style with the given path.

        Args:
            path (str): The file path to save the persisted data.
        """
        self.path = path

    def encode(self, object):
        """Encode the given object to a JSON string.

        Args:
            object: The object to encode.

        Returns:
            str: The JSON string representation of the object.
        """
        return json.dumps(object)

    def decode(self, string):
        """Decode the given JSON string to an object.

        Args:
            string (str): The JSON string to decode.

        Returns:
            object: The Python object representation of the JSON string.
       
