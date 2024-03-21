# -*- twisted.conch.test.test_mixin -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import time

from twisted.internet import reactor, protocol
from twisted.trial import unittest
from twisted.test.proto_helpers import StringTransport
from twisted.conch import mixin

class TestBufferingProto(mixin.BufferingMixin):
    scheduled = False
    rescheduled = 0

    def schedule(self):
        self.scheduled = True
        return object()

    def reschedule(self, token):
        self.rescheduled += 1

class BufferingTest(unittest.TestCase):
    """
    Test the buffering behavior of the BufferingMixin.
    """

    def setUp(self):
        self.p = TestBufferingProto()
        self.t = self.p.transport = StringTransport()

    def tearDown(self):
        self.t.clear()
        reactor.stop()

    def testBuffering(self):
        self.failIf(self.p.scheduled)

        L = ['foo', 'bar', 'baz', 'quux']

        self.p.write('foo')
        self.failUnless(self.p.scheduled)
        self.failIf(self.p.rescheduled)

        for s in L:
            n = self.p.rescheduled
            self.p.write(s)
            self.assertEqual(self.p.rescheduled, n + 1)
            self.assertEqual
