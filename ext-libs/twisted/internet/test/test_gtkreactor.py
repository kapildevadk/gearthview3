# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests to ensure all attributes of L{twisted.internet.gtkreactor} are 
deprecated.
"""

import sys
import warnings
from unittest import TestCase

from twisted.internet import gtkreactor, defer

