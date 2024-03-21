# -*- test-case-name: twisted.conch.test.test_openssh_compat -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Factory for reading openssh configuration files: public keys, private keys, and
moduli file.
"""

import os
import errno
from contextlib import suppress
from twisted.python import log
from twisted.python.util import runAsEffectiveUser
from twisted.conch.ssh import keys, factory, common
from twisted.conch.openssh_compat import primes


class OpenSSHFactory(factory.SSHFactory):
    """
    A factory for creating SSH servers using OpenSSH-style keys and configuration.
    """
    dataRoot = '/usr/local/etc'
    dataSubdir = 'ssh'
    moduliRoot = '/usr/local/etc'

    def getPublicKeys(self):
        """
        Return the server public keys.
        """
        keys_by_type = {}
        for filename in os.listdir(os.path.join(self.dataRoot, self.dataSubdir)):
            if filename.startswith('ssh_host_') and filename.endswith('.pub'):
                filepath = os.path.join(self.dataRoot, self.dataSubdir, filename)
                if not os.path.exists(filepath):
                    log.msg(f'File does not exist: {filepath}')
                    continue
                try:
                    key = keys.Key.fromFile(filepath)
                    key_type = common.getNS(key.blob())[0]
                    keys_by_type[key_type] = key
                except Exception as e:
                    log.msg(f'Error reading public key file {filename}: {e}')
        return keys_by_type

    def getPrivateKeys(self):
        """
        Return the server private keys.
        """
        private_keys_by_type = {}
        for filename in os.listdir(os.path.join(self.dataRoot, self.dataSubdir)):
            if filename.startswith('ssh_host_') and filename.endswith('_key'):
                filepath = os.path.join(self.dataRoot, self.dataSubdir, filename)
                if not os.path.exists(filepath):
                    log.msg(f'File does not exist: {filepath}')
                    continue
                try:
                    with open(filepath, 'r') as f:
                        key_data = f.read()
                except IOError as e:
                    if e.errno == errno.EACCES:
                        # Not allowed, let's switch to root
                        with suppress(IOError):
                            key = runAsEffectiveUser(0, 0, keys.Key.fromFile, filepath)
                            key_type = keys.objectType(key.keyObject)
                            private_keys_by_type[key_type] = key
                    else:
                        raise
                except Exception as e:
                    log.msg(f'Error reading private key file {filename}: {e}')
                else:
                    try:
                        key = keys.Key.fromData(key_data)
                    except Exception as e:
                        log.msg(f'Error parsing private key data: {e}')
                    else:
                        key_type = keys.objectType(
