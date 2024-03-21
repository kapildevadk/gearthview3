# -*- test-case-name: twisted.test.test_strcred -*-
#
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Anonymous Cred plugin for Twisted.
"""

from zope.interface import implementer

from twisted import plugin
from twisted.cred.checkers import AllowAnonymousAccess
from twisted.cred.strcred import ICheckerFactory
from twisted.cred.credentials import IAnonymous


class AnonymousCheckerFactory(object):
    """
    Generates checkers that will authenticate an anonymous request.
    """
    _serviceName = "anonymous-cred-plugin"
    authType = 'anonymous'
    authHelp = """
    This allows anonymous authentication for servers that support it.

    For more information, see:
    <https://twistedmatrix.com/trac/wiki/TwistedCredentials#anonymous-authentication>
    """
    argStringFormat = 'No arguments required.'
    credentialInterfaces = (IAnonymous,)
    _realm = "Twisted Anonymous"

    def generateChecker(self, argstring=''):
        return AllowAnonymousAccess(realm=self._realm)

    @property
    def description(self):
        """
        A brief description of the plugin.
        """
        return "Anonymous Cred plugin for Twisted."


theAnonymousCheckerFactory = AnonymousCheckerFactory()

