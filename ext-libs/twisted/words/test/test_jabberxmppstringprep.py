# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import unittest
from twisted.words.protocols.jabber.xmpp_stringprep import (
    nodeprep,
    resourceprep,
    nameprep,
    crippled,
)

class XMPPStringPrepTest(unittest.TestCase):
    """
    Tests for XMPP stringprep profiles.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the test case.
        """
        super().__init__(*args, **kwargs)
        self.no_resourceprep_tests = crippled

    def test_resourceprep(self):
        """
        Test the resourceprep stringprep profile.
        """
        self.assertEqual(resourceprep.prepare(u"resource"), u"resource")
        self.assertNotEqual(resourceprep.prepare(u"Resource"), u"resource")
        self.assertEqual(resourceprep.prepare(u" "), u" ")

        if self.no_resourceprep_tests:
            return

        resourceprep_extra_tests = [
            (u"Henry \u2163", u"Henry IV"),
            (u"foo\xad\u034f\u1806\u180b bar\u200b\u2060 baz\ufe00\ufe08\ufe0f\ufeff", u"foobarbaz"),
            (u"\u00a0", u" "),
            (u"\u1680", UnicodeError),
            (u"\u2000", u" "),
            (u"\u200b", u""),
            (u"\u0010\u007f", UnicodeError),
            (u"\u0085", UnicodeError),
            (u"\u180e", UnicodeError),
            (u"\ufeff", u""),
            (u"\uf123", UnicodeError),
            (u"\U000f1234", UnicodeError),
            (u"\U0010f234", UnicodeError),
            (u"\U0008fffe", UnicodeError),
            (u"\U0010ffff", UnicodeError),
            (u"\udf42", UnicodeError),
            (u"\ufffd", UnicodeError),
            (u"\u2ff5", UnicodeError),
            (u"\u0341", u"\u0301"),
            (u"\u200e", UnicodeError),
            (u"\u202a", UnicodeError),
            (u"\U000e0001", UnicodeError),
            (u"\U000e0042", UnicodeError),
            (u"foo\u05bebar", UnicodeError),
            (u"foo\ufd50bar", UnicodeError),
            # (u"foo\ufb38bar", u"foo\u064ebar"),
            (u"\u06271", UnicodeError),
            (u"\u06271\u0628", u"\u06271\u0628"),
            (u"\U000e0002", UnicodeError),
        ]

        for input, expected in resourceprep_extra_tests:
            with self.subTest(input=input):
                if isinstance(expected, str):
                    self.assertEqual(resourceprep.prepare(input), expected)
                else:
                    self.assertRaises(UnicodeError, resourceprep.prepare, input)

    @unittest.skipIf(crippled, "Skipping nodeprep tests")
    def test_nodeprep(self):
        """
        Test the nodeprep stringprep profile.
        """
        self.assertEqual(nodeprep.prepare(u"user"), u"user")
        self.assertEqual(nodeprep.prepare(u"User"), u"user")
        self.assertRaises(UnicodeError, nodeprep.prepare, u"us&er")

    def test_nodeprep_unassigned_unicode_3_2(self):
        """
        Make sure unassigned code points from Unicode 3.2 are rejected.
        """
        self.assertRaises(UnicodeError, nodeprep.prepare, u"\u1d39")

    @unittest.skipIf(crippled, "Skipping nameprep tests")
    def test_nameprep(self):
        """
        Test the nameprep stringprep profile.
        """
        self.assertEqual(nameprep.prepare(u"example.com"), u"example.com")
        self.assertEqual(nameprep.prepare(u"Example.com"), u"example.com")
        self.assertRaises(UnicodeError, nameprep.prepare, u"ex@mple.com")
        self.assertRaises(UnicodeError, nameprep.prepare, u"-example.com")
        self.assertRaises(UnicodeError, nameprep.prepare, u"example-.com")

        nameprep_extra_tests = [
            (u"stra\u00dfe.example.com", u"strasse.example.com"),
        ]

        for input, expected in nameprep_extra_
