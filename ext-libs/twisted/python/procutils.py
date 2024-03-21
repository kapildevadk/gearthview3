# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Utilities for dealing with processes.
"""

import os

def which(name, flags=os.X_OK):
    """Search PATH for executable files with the given name.
    
    On newer versions of MS-Windows, the PATHEXT environment variable will be
    set to the list of file extensions for files considered executable. This
    will normally include things like ".EXE". This function will also find files
    with the given name ending with any of these extensions.

    On MS-Windows the only flag that has any meaning is os.F_OK. Any other
    flags will be ignored.
    
    @type name: str
    @param name: The name for which to search.
    
    @type flags: int
    @param flags: Arguments to os.access.
    
    @rtype: list
    @return: A list of the full paths to files found, in the
    order in which they were found.
    """

