# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.internet.application}.
"""

from twisted.trial import unittest
from twisted.internet import reactor, defer, application


class ApplicationTests(unittest.TestCase):
    """
    Test cases for the L{twisted.internet.application} module.
    """

    def setUp(self):
        """
        Set up a new L{twisted.internet.application.Application} instance for each test case.
        """
        self.app = application.Application("test-app")

    def test_serviceNames(self):
        """
        Test that the L{serviceNames} method returns an empty list for a new application.
        """
        self.assertEqual(self.app.serviceNames(), [])

    def test_addService(self):
        """
        Test that the L{addService} method adds a service to the application.
        """
        name = "test-service"
        service = defer.DeferredService()
        self.app.addService(name, service)
        self.assertIn(name, self.app.serviceNames())

    def test_openAndClose(self):
        """
        Test that the L{open} and L{close} methods work as expected.
        """
        d = defer.Deferred()
        service = defer.DeferredService()
        service.addCallback(lambda _: d.callback(None))
        name = "test-service"
        self.app.addService(name, service)

        @defer.inlineCallbacks
        def test():
            yield self.app.open()
            self.assertTrue(self.app.running)
            yield service
            self.assertFalse(self.app.running)
            yield self.app.close()
            self.assertFalse(self.app.running)

        return test()


if __name__ == "__main__":

