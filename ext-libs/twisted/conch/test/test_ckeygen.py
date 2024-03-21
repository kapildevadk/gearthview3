# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.conch.scripts.ckeygen}.
"""

import getpass
import sys
from io import StringIO
from unittest.mock import patch

import pyasn1
import six
from twisted.conch.ssh.keys import Key, BadKeyError
from twisted.conch.scripts.ckeygen import (
    displayPublicKey, printFingerprint, _saveKey)
from twisted.conch.test.keydata import (
    publicRSA_openssh, privateRSA_openssh, privateRSA_openssh_encrypted)
from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase


class KeyGenTests(TestCase):
    """
    Tests for various functions used to implement the I{ckeygen} script.
    """
    def setUp(self):
        """
        Patch C{sys.stdout} with a L{StringIO} instance to tests can make
        assertions about what's printed.
        """
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        """
        Reset C{sys.stdout} after each test.
        """
        sys.stdout = sys.__stdout__

    def test_print_fingerprint(self):
        """
        L{printFingerprint} writes a line to standard out giving the number of
        bits of the key, its fingerprint, and the basename of the file from it
        was read.
        """
        filename = self.mktemp()
        FilePath(filename).setContent(publicRSA_openssh)

        printFingerprint({'filename': filename})

        expected_output = (
            f'768 {printFingerprint({"filename": filename})} '
            f'{filename.split("/")[-1]}'
        )

        self.assertEqual(self.stdout.getvalue().strip(), expected_output)

    def test_save_key(self):
        """
        L{_saveKey} writes the private and public parts of a key to two
        different files and writes a report of this to standard out.
        """
        base = FilePath(self.mktemp())
        base.makedirs()
        filename = base.child('id_rsa').path

        key = Key.fromString(privateRSA_openssh)

        _saveKey(
            key.keyObject,
            {'filename': filename, 'pass': 'passphrase'}
        )

        expected_output = (
            f"Your identification has been saved in {filename}\n"
            f"Your public key has been saved in {filename}.pub\n"
            f"The key fingerprint is:\n"
            f"{printFingerprint({'filename': filename})}\n"
        )

        self.assertEqual(self.stdout.getvalue().strip(), expected_output)

        with open(base.child('id_rsa'), 'r') as f:
            restored_key = Key.fromString(f.read(), None, 'passphrase')

        self.assertEqual(restored_key, key)

        with open(base.child('id_rsa.pub'), 'r') as f:
            restored_pub_key = Key.fromString(f.read())

        self.assertEqual(restored_pub_key, key.public())

    def test_display_public_key(self):
        """
        L{displayPublicKey} prints out the public key associated with a given
        private key.
        """
        filename = self.mktemp()
        pub_key = Key.fromString(publicRSA_openssh)
        FilePath(filename).setContent(privateRSA_openssh)

        with patch('getpass.getpass', return_value=''):
            displayPublicKey({'filename': filename})

        self.assertEqual(
            self.stdout.getvalue().strip(),
            pub_key.toString('openssh')
        )

    def test_display_public_key_encrypted(self):
        """
        L{displayPublicKey} prints out the public key associated with a given
        private key using the given passphrase when it's encrypted.
        """
        filename = self.mktemp()
        pub_key = Key.fromString(publicRSA_openssh)
        FilePath(filename).setContent(privateRSA_openssh_encrypted)

        with patch('getpass.getpass', return_value='encrypted'):
            displayPublicKey({'filename': filename})

        self.assertEqual(
            self.stdout.getvalue().strip(),
            pub_key.toString('openssh')
        )

    def test_display_public_key_encrypted_passphrase_prompt(self):
        """
        L{displayPublicKey} prints out the public key associated with a given
        private key, asking for the passphrase when it's encrypted.
        """
        filename = self.mktemp()
        pub_key = Key.fromString(publicRSA_openssh)
        FilePath(filename).setContent(privateRSA_openssh_encrypted)

        with patch('getpass.getpass', return_value='encrypted'):
            displayPublicKey({'filename': filename})

        self.assertEqual(
            self.stdout.getvalue().strip(),
            pub_key.toString('openssh')
        )

    def test_display_public_key_wrong_passphrase(self):
        """
        L{displayPublicKey} fails with a L{BadKeyError} when trying to decrypt
        an encrypted key with the wrong password.
        """
        filename = self.mkt
