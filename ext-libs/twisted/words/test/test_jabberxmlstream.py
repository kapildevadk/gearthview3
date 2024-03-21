# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.words.protocols.jabber.xmlstream}.
"""

import os
import unittest
from zope.interface.verify import verifyObject
from twisted.internet import defer, task, reactor
from twisted.internet.error import ConnectionLost
from twisted.internet.interfaces import IProtocolFactory
from twisted.python import failure
from twisted.test import proto_helpers
from twisted.words.test.test_xmlstream import GenericXmlStreamFactoryTestsMixin
from twisted.words.xish import domish
from twisted.words.protocols.jabber import error, ijabber, jid, xmlstream


NS_XMPP_TLS = 'urn:ietf:params:xml:ns:xmpp-tls'


class HashPasswordTest(unittest.TestCase):
    """
    Tests for L{xmlstream.hashPassword}.
    """

    def test_basic(self):
        """
        The sid and secret are concatenated to calculate sha1 hex digest.
        """
        hash = xmlstream.hashPassword(b"12345", b"secret")
        self.assertEqual('99567ee91b2c7cabf607f10cb9f4a3634fa820e0', hash)

    def test_sid_not_unicode(self):
        """
        The session identifier must be a unicode object.
        """
        with self.assertRaises(TypeError):
            xmlstream.hashPassword(b"\xc2\xb92345", b"secret")

    def test_password_not_unicode(self):
        """
        The password must be a unicode object.
        """
        with self.assertRaises(TypeError):
            xmlstream.hashPassword(b"12345", b"secr\xc3\xa9t")

    def test_unicode_secret(self):
        """
        The concatenated sid and password must be encoded to UTF-8 before hashing.
        """
        hash = xmlstream.hashPassword(b"12345", b"secr\u00e9t")
        self.assertEqual('659bf88d8f8e179081f7f3b4a8e7d224652d2853', hash)


class IQTest(unittest.TestCase):
    """
    Tests both IQ and the associated IIQResponseTracker callback.
    """

    def setUp(self):
        self.authenticator = xmlstream.ConnectAuthenticator('otherhost')
        self.authenticator.namespace = 'testns'
        self.xmlstream = xmlstream.XmlStream(self.authenticator)
        self.clock = task.Clock()
        self.xmlstream._callLater = self.clock.callLater
        self
