# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.words.xmpproutertap}.
"""

from twisted.application import internet
from twisted.trial import unittest
from twisted.words import xmpproutertap as tap
from twisted.words.protocols.jabber import component
import os

class XMPPRouterTapTest(unittest.TestCase):

    def setUp(self):
        self.opt = tap.Options()

    def test_port(self):
        """
        The port option is recognized as a parameter.
        """
        self.opt.parseOptions(['--port', '7001'])
        self.assertEqual(self.opt['port'], '7001')

    def test_portDefault(self):
        """
        The port option has '5347' as default value.
        """
        self.opt.parseOptions([])
        self.assertEqual(self.opt['port'], 'tcp:5347:interface=127.0.0.1')

    def test_makeService_default_port(self):
        """
        The service gets set up with the default port when the --port option is not provided.
        """
        self.opt.parseOptions([])
        s = tap.makeService(self.opt)
        self.assertEqual(s.endpoint._port, 5347)

    def test_makeService_port_type(self):
        """
        The --port option accepts a string that can be converted to an integer.
        """
        self.opt.parseOptions(['--port', '7001'])
        self.assertIsInstance(int(self.opt['port']), int)

    def test_makeService_port_invalid(self):
        """
        The --port option raises a ValueError when the provided value cannot be converted to an integer.
        """
        with self.assertRaises(ValueError):
            self.opt.parseOptions(['--port', 'notanumber'])

    def test_secret(self):
        """
        The secret option is recognized as a parameter.
        """
        self.opt.parseOptions(['--secret', 'hushhush'])
        self.assertEqual(self.opt['secret'], 'hushhush')

    def test_secretDefault(self):
        """
        The secret option has 'secret' as default value.
        """
        self.opt.parseOptions([])
        self.assertEqual(self.opt['secret'], 'secret')

    def test_makeService_default_secret(self):
        """
        The service gets set up with the default secret when the --secret option is not provided.
        """
