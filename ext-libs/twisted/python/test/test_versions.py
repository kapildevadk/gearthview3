# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.versions}.
"""

from __future__ import division, absolute_import

import sys
import operator
from io import BytesIO
import re

from twisted.python.versions import getVersionString, IncomparableVersions
from twisted.python.versions import Version, _inf
from twisted.python.filepath import FilePath
from twisted.trial.unittest import SynchronousTestCase as TestCase

VERSION_4_ENTRIES = b"""\
<?xml version="1.0" encoding="utf-8"?>
<wc-entries
   xmlns="svn:">
<entry
   committed-rev="18210"
   name=""
   committed-date="2006-09-21T04:43:09.542953Z"
   url="svn+ssh://svn.twistedmatrix.com/svn/Twisted/trunk/twisted"
   last-author="exarkun"
   kind="dir"
   uuid="bbbe8e31-1
