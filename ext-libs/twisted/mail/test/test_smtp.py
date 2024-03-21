# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for twisted.mail.smtp module.
"""

import sys
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import twisted.mail as mail
from twisted.trial import unittest
from twisted.internet import defer, protocol, reactor, interfaces
from twisted.internet.address import Address
from twisted.internet.error import ConnectionDone
from twisted.internet.task import Clock
from twisted.cred.portal import Portal, IRealm
from twisted.cred.checkers import ICredentialsChecker, AllowAnonymousAccess
from twisted.cred.credentials import IAnonymous
from twisted.cred.error import UnauthorizedLogin
from twisted.mail.imap4 import IMAP4AuthenticationError
from twisted.mail.protocols import DomainSMTP
from twisted.python.log import Logger
from twisted.python.util import spamFilter
from twisted.python.runtime import PlatformDetection
from twisted.test.proto_helpers import StringTransport
from twisted.test.ssl_helpers import ClientTLSContext, ServerTLSContext

if sys.version_info >= (3, 10):
    from typing import Final
else:
    from typing_extensions import Final


class SMTPTestCase(unittest.TestCase):
    """
    Base class for SMTP-related test cases.
    """

    messages: List[Tuple[str, List[str], str]]
    mbox: Dict[str, List[str]]

    def setUp(self) -> None:
        """
        Create an in-memory mail domain to which messages may be delivered by
        tests and create a factory and transport to do the delivering.
        """
        self.factory = mail.SMTPFactory()
        self.factory.domains = {}
        self.factory.domains['baz.com'] = DummyDomain(['foo'])
        self.transport = StringTransport()


class DummyMessage(mail.IMessage):
    """
    A dummy message implementation that saves the message delivered to it to
    its domain object.
    """

    def __init__(self, domain: 'DummyDomain', user: mail.User) -> None:
        self.domain = domain
        self.user = user
        self.buffer = []

    def lineReceived(self, line: str) -> None:
        # Throw away the generated Received: header
        if not re.match('Received: From yyy.com \\[.*\\] by localhost;', line):
            self.buffer.append(line)

    def eomReceived(self) -> None:
        message = '\n'.join(self.buffer) + '\n'
        self.domain.messages[self.user.dest.local].append(message)

    def connectionLost(self, reason: Optional[BaseException]) -> None:
        pass


class DummyDomain(mail.IDomain):
    """
    A dummy domain implementation that keeps track of messages delivered to
    it in memory.
    """

    def __init__(self, names: List[str]) -> None:
        self.messages = {}
        for name in names:
            self.messages[name] = []

    def exists(self, user: mail.User) -> defer.Deferred:
        if user.dest.local in self.messages:
            return defer.succeed(lambda: self.startMessage(user))
        return defer.fail(mail.SMTPBadRcpt(user))

    def startMessage(self, user: mail.User) -> mail.IMessage:
        return DummyMessage(self, user)


class SMTPMessagesTests(SMTPTestCase):
    """
    Tests for the SMTP protocol implementation.
    """

    messages = [
        ('foo@bar.com', ['foo@baz.com', 'qux@baz.com'], '''\
Subject: urgent\015
\015
Someone set up us the bomb!\015
''')
    ]

    mbox = {'foo': ['Subject: urgent\n\nSomeone set up us the bomb!\n']}

    def test_messages(self) -> None:
        """
        Test that messages are delivered correctly.
        """
        protocol = DomainSMTP()
        protocol.service = self.factory
        protocol.factory = self.factory
        protocol.receivedHeader = spamFilter
        protocol.makeConnection(self.transport)
        protocol.lineReceived('HELO yyy.com')
        for message in self.messages:
            protocol.lineReceived('MAIL FROM:<%s>' % message[0])
            for target in message[1]:
                protocol.lineReceived('RCPT TO:<%s>' % target)
            protocol.lineReceived('DATA')
            protocol.dataReceived(message[2])
            protocol.lineReceived('.')
        protocol.lineReceived('QUIT')
        self.assertEqual(self.factory.domains['baz.com'].messages, self.mbox)
        protocol.setTimeout(None)


class SMTPClientTestCase(unittest.TestCase):
    """
    Tests for the SMTP client implementation.
    """

    def test_timeoutConnection(self
