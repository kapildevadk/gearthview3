# -*- test-case-name: twisted.test.test_strcred -*-
#
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Cred plugin for ssh key login
"""

from zope.interface import implements

from twisted import plugin
from twisted.cred.strcred import ICheckerFactory
from twisted.cred.credentials import ISSHPrivateKey
from twisted.conch.checkers import SSHPublicKeyDatabase

__author__ = "Twisted Matrix Laboratories"
__license__ = "MIT"

sshKeyCheckerFactoryHelp = """
This allows SSH public key authentication, based on public keys listed in
authorized_keys and authorized_keys2 files in user .ssh/ directories.
"""


class SSHKeyCheckerFactory(object):
    """
    Generates checkers that will authenticate a SSH public key
    """
    implements(ICheckerFactory, plugin.IPlugin)
    authType = 'sshkey'
    authHelp = sshKeyCheckerFactoryHelp
    argStringFormat = 'No argstring required.'
    credentialInterfaces = (ISSHPrivateKey,)

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.credentialInterfaces = (ISSHPrivateKey,)

    def generateChecker(self, argstring=''):
        """
        This checker factory ignores the argument string. Everything
        needed to authenticate users is pulled out of the public keys
        listed in user .ssh/ directories.
        """
        return SSHPublicKeyDatabase()


if __name__ == '__main__':
    print(sshKeyCheckerFactoryHelp)
