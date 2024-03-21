# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{SSHTransportAddrress} in ssh/address.py
"""

from typing import Any

from twisted.trial import unittest
from twisted.internet.address import IPv4Address
from twisted.internet.test.test_address import AddressTestCaseMixin

from twisted.conch.ssh.address import SSHTransportAddress


class SSHTransportAddressTestCase(unittest.TestCase, AddressTestCaseMixin):
    """
    Tests for L{twisted.conch.ssh.address.SSHTransportAddress}.
    """

    def _stringRepresentation(self, stringFunction: Any) -> None:
        """
        The string representation of C{SSHTransportAddress} should be
        "SSHTransportAddress(<stringFunction on address>)".
        """
        addr = self.buildAddress()
        string_value = stringFunction(addr)
        address_value = stringFunction(addr.address)
        self.assertEqual(string_value, f"SSHTransportAddress({address_value})")

    def buildAddress(self) -> SSHTransportAddress:
        """
        Create an arbitrary new C{SSHTransportAddress}.  A new instance is
        created for each call, but always for the same address.
        """
        return SSHTransportAddress(IPv4Address("TCP", "127.0.0.1", 22))

    def buildDifferentAddress(self) -> SSHTransportAddress:
        """
        Like C{buildAddress}, but with a different fixed address.
        """
        return SSHTransportAddress(IPv4Address("TCP", "127.0.0.2", 22))

    def test_equality(self) -> None:
        """
        Test the equality of two C{SSHTransportAddress} objects.
        """
        addr1 = self.buildAddress()
        addr2 = self.buildAddress()
        addr3 = self.buildDifferentAddress()
        self.assertEqual(addr1, addr1)
        self.assertEqual(addr1, addr2)
        self.assertNotEqual(addr1, addr3)
