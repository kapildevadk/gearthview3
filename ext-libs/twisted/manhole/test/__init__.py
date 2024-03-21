# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.manhole}.
"""

import unittest
from twisted.manhole import Manhole


class ManholeTests(unittest.TestCase):
    def setUp(self):
        self.manhole = Manhole()

    def test_something(self):
        # Add your test case here
        pass


if __name__ == '__main__':
    unittest.main()
