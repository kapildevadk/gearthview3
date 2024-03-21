# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.words.protocols.jabber.jid}.
"""

from twisted.trial import unittest

from twisted.words.protocols.jabber import jid

class JIDParsingTest(unittest.TestCase):
    """
    Test cases for parsing JIDs.
    """

    def test_parse(self):
        """
        Test different forms of JIDs.
        """
        # Basic forms
        self.assertEqual(jid.parse("user@host/resource"),
                          ("user", "host", "resource"))
        self.assertEqual(jid.parse("user@host"),
                          ("user", "host", None))
        self.assertEqual(jid.parse("host"),
                          (None, "host", None))
        self.assertEqual(jid.parse("host/resource"),
                          (None, "host", "resource"))

        # More interesting forms
        self.assertEqual(jid.parse("foo/bar@baz"),
                          (None, "foo", "bar@baz"))
        self.assertEqual(jid.parse("boo@foo/bar@baz"),
                          ("boo", "foo", "bar@baz"))
        self.assertEqual(jid.parse("boo@foo/bar/baz"),
                          ("boo", "foo", "bar/baz"))
        self.assertEqual(jid.parse("boo/foo@bar@baz"),
                          (None, "boo", "foo@bar@baz"))
        self.assertEqual(jid.parse("boo/foo/bar"),
                          (None, "boo", "foo/bar"))
        self.assertEqual(jid.
