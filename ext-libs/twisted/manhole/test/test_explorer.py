# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.manhole.explorer}.
"""

import unittest
from twisted.manhole.explorer import (
    CRUFT_WatchyThingie,
    ExplorerImmutable,
    Pool,
    _WatchMonkey,
)


class Foo:
    """
    Test helper.
    """


class PoolTestCase(unittest.TestCase):
    """
    Tests for the Pool class.
    """

    def test_instanceBuilding(self) -> None:
        """
        If the object is not in the pool a new instance is created and
        returned.
        """
        p = Pool()
        e = p.getExplorer(123, "id")
        self.assertIsInstance(e, ExplorerImmutable)
        self.assertEqual(e.value, 123)
        self.assertEqual(e.identifier, "id")

