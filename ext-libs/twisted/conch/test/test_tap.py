# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.conch.tap}.
"""

import os
import sys

try:
    import Crypto.Cipher.DES3
except:
    Crypto = None

try:
    import pyasn1
except ImportError:
    pyasn1 = None

try:
    from twisted.conch import unix
except ImportError:
    unix = None

if Crypto and pyasn1 and unix:
    from twisted.conch import tap
    from twisted.conch.openssh_compat.factory import OpenSSHFactory
else:
    OpenSSHFactory = None

from twisted.application.internet import StreamServerEndpointService
from twisted.cred import error
from twisted.cred.credentials import IPluggableAuthenticationModules
from twisted.cred.credentials import ISSHPrivateKey
from twisted.cred.credentials import IUsernamePassword
from twisted.cred.credentials import UsernamePassword
from twisted.trial.unittest import TestCase

if hasattr(os, "mktemp"):
    def make_temp_file():
        return os.mktemp()
else:
    make_temp_file = None

if hasattr(sys, "monkeypatch"):
    def patch(module, name, value):
        getattr(module, "__builtins__").__setitem__(name, value)
else:
    patch = None


class MakeServiceTests(TestCase):
    """
    Tests for L{tap.makeService}.
    """

    if not Crypto:
        skip = "can't run w/o PyCrypto"

    if not pyasn1:
        skip = "Cannot run without PyASN1"

    if not unix:
        skip = "can't run on non-posix computers"

    usernamePassword = ("iamuser", "thisispassword")

    def setUp(self):
        """
        Create a file with two users.
        """
        if make_temp_file is None:
            self.skipTest("os.mktemp not available")

        self.filename = make_temp_file()
        self.create_test_user()
        self.options = tap.Options()

    def create_test_user(self):
        """
        Create a test user in the temporary file.
        """
        with open(self.filename, "wb+") as f:
            f.write(":".join(self.usernamePassword))

    def tearDown(self):
        """
        Clean up the temporary file created in the setUp function.
        """
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_basic(self):
        """
        L{tap.makeService} returns a L{StreamServerEndpointService} instance
        running on TCP port 22, and the linked protocol factory is an instance
        of L{OpenSSHFactory}.
        """
        if OpenSSHFactory is None:
            self.skipTest("OpenSSHFactory not available")

        config = tap.Options()
        service = tap.makeService(config)
        self.assertIsInstance(service, StreamServerEndpointService)
        self.assertEqual(service.endpoint._port, 22)
        self.assertIsInstance(service.factory, OpenSSHFactory)

    def test_default_auth_checkers(self):
        """
        Make sure that if the C{--auth} command-line option is not passed,
        the default checkers are (for backwards compatibility): SSH, UNIX, and
        PAM if available.
        """
        num_checkers = 2
        try:
            from twisted.cred import pamauth

            self.assertIn(
                IPluggableAuthenticationModules,
                self.options["credInterfaces"],
                "PAM should be one of the modules",
            )
            num_checkers += 1
        except ImportError:
            pass

        self.assertIn(ISSHPrivateKey, self.options["credInterfaces"],
            "SSH should be one of the default checkers")
        self.assertIn(IUsernamePassword, self.options["credInterfaces"],
            "UNIX should be one of the default checkers")
        self.assertEqual(num_checkers, len(self.options["credCheckers"]),
            "There should be %d checkers by default" % (num_checkers,))

    def test_auth_checker_added(self):
        """
        The C{--auth} command-line option will add a checker to the list of
        checkers, and it should be the only auth checker.
        """
        self.options.parseOptions(["--auth", "file:" + self.filename])
        self.assertEqual(len(self.options["credCheckers"]), 1)

    def test_multiple_auth_checkers_added(self):
        """
        Multiple C{--auth} command-line options will add all checkers specified
        to the list of checkers, and there should only be the specified auth
        checkers (no default checkers).
        """
        self.options.parseOptions(
            "
