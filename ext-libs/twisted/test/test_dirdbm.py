# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for dirdbm module.
"""

import os
import shutil
import glob
import pytest
from typing import Any, Dict, Set, Tuple

from twisted.trial import unittest
from twisted.persisted import dirdbm


class DirdbmTestCase(unittest.TestCase):
    """
    Test cases for dirdbm module.
    """

    dirdbm_class = dirdbm.DirDBM

    @pytest.mark.parametrize("items", [(('abc', 'foo'), ('/lalal', '\000\001'), ('\000\012', 'baz'))])
    def setUp(self, items: Tuple[Tuple[str, str], ...]) -> None:
        """
        Set up the test case.

        :param items: Items to add to the dirdbm.
        """
        self.path = self.mktemp()
        self.dbm = self.dirdbm_class(self.path)
        self.items = items

        # insert keys
        keys = []
        values = set()
        for k, v in self.items:
            self.dbm[k] = v
            keys.append(k)
            values.add(v)
        keys.sort()

    def tearDown(self) -> None:
        """
        Clean up the test case.
        """
        shutil.rmtree(self.path)

    def test_all(self) -> None:
        """
        Test the 'all' method.
        """
        k = "//==".decode("base64")
        self.dbm[k] = "a"
        self.dbm[k] = "a"
        self.assertEqual(self.dbm[k], "a")

    def test_rebuild_interaction(self) -> None:
        """
        Test the interaction with the rebuild module.
        """
        from twisted.persisted import dirdbm
        from twisted.python import rebuild

        s = dirdbm.Shelf('dirdbm.rebuild.test')
        s["key"] = "value"
        rebuild.rebuild(dirdbm)
        # print s['key']

    def test_dbm(self) -> None:
        """
        Test the basic functionality of the dirdbm.
        """
        # check keys(), values() and items()
        dbkeys = list(self.dbm.keys())
        dbvalues = set(self.dbm.values())
        dbitems = set(self.dbm.items())
        dbkeys.sort()
        items = set(self.items)
        self.assertEqual(keys, dbkeys)
        self.assertEqual(values, dbvalues)
        self.assertEqual(items, dbitems)

        copy_path = self.mktemp()
        d2 = self.dbm.copyTo(copy_path)

        copykeys = list(d2.keys())
        copyvalues = set(d2.values())
        copyitems = set(d2.items())
        copykeys.sort()

        self.assertEqual(dbkeys, copykeys)
        self.assertEqual(dbvalues, copyvalues)
        self.assertEqual(dbitems, copyitems)

        d2.clear()
        self.assertEqual(len(d2.keys()), len(d2.values()), len(d2.items()), 0)
        shutil.rmtree(copy_path)

        # delete items
        for k, v in self.items:
            del self.dbm[k]
        self.assertEqual(len(self.dbm.keys()), 0)
        self.assertEqual(len(self.dbm.values()), 0)
        self.assertEqual(len(self.dbm.items()), 0)

    def test_modification_time(self) -> None:
        """
        Test the modification time of the dirdbm.
        """
        self.dbm["k"] = "v"
        self.assertAlmostEqual(
            time.time(), self.dbm.getModificationTime("k"), delta=3
        )

    def test_recovery(self) -> None:
        """
        Test recovery from directory after a faked crash.
        """
        k = self.dbm._encode("key1")
        with open(os.path.join(self.path, k + ".rpl"), "wb") as f:
            f.write(b"value")

        k2 = self.dbm._encode("key2")
        with open(os.path.join(self.path, k2), "wb") as f:
            f.write(b"correct")

        with open(os.path.join(self.path, k2 + ".rpl"), "wb") as f:
            f.write(b"wrong")

        with open(os.path.join(self.path, "aa.new"), "wb") as f:
            f.write(b"deleted")

        dbm = self.dirdbm_class(self.path)
        self.assertEqual(dbm["key1"], "value")
        self.assertEqual(dbm["key2"], "correct")
        self.assertFalse(glob.glob(os.path.join(self.path, "*.new")))
        self.assertFalse(glob.glob(os.path.join(self.path, "*.rpl")))

    def test_non_string_keys(self) -> None:
        """
        Test that only string keys are supported.
        """
        self.assertRaises(
            AssertionError, self
