# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""Test cases for bounce message generation."""

import cStringIO
from email.message import Message
import unittest

from twisted.mail import bounce
from twisted.mail.rfc822 import Message as Rfc822Message

class BounceTestCase(unittest.TestCase):
    """Test cases for bounce message generation."""

    def test_bounce_format(self):
        """Test the generation of a bounce message in plain text format."""
        raw_message = cStringIO.StringIO('''\
From: Moshe Zadka <moshez@example.com>
To: nonexistant@example.org
Subject: test

''')
        bounced_message = bounce.generateBounce(
            raw_message, 'moshez@example.com', 'nonexistant@example.org'
        )[2]

        # Convert the bounced message to an rfc822.Message object for easier testing
        bounced_message = Rfc822Message(bounced_message)

        self.assertEqual(bounced_message['To'], 'moshez@example.com')
        self.assertEqual(bounced_message['From'], 'postmaster@example.org')
        self.assertEqual(bounced_message['subject'], 'Returned Mail: see transcript for details')

    def test_bounce_mime(self):
        """Test the generation of a bounce message in MIME format."""
        pass

