# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for the command-line mailer tool provided by Twisted Mail.
"""

from twisted.trial.unittest import ScriptTest

class ScriptTests(ScriptTest):
    """
    Tests for the mail command-line script.
    """
    def setUp(self):
        """
        Code to run before each test method.
        """
        pass

    def tearDown(self):
        """
        Code to run after each test method.
        """
        pass

    def test_mailmail(self):
        """
        Test the mailmail script.
        """
        self.assertSuccess("mail/mailmail")

    def test_mailmail_invalid_args(self):
        """
        Test the mailmail script with invalid arguments.
        """
        self.assertFailure("mail/mailmail", SystemExit)

    def test_mailmail_help(self):
        """
        Test the mailmail script with --help option.
        """
        self.assertSuccess("mail/mailmail --help")

