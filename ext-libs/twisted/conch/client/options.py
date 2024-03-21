# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from typing import List, Tuple, Dict, Optional

from twisted.conch.ssh.transport import SSHClientTransport, SSHCiphers
from twisted.python import usage

class ConchOptions(usage.Options):
    """
    Options for the Twisted Conch SSH client.
    """

    optParameters = [
        ['user', 'l', None, 'Log in using this user name.'],
        ['identity', 'i', None],
        ['ciphers', 'c', None],
        ['macs', 'm', None],
        ['port', 'p', None, 'Connect to this port.  Server must be on the same port.'],
        ['option', 'o', None, 'Ignored OpenSSH options'],
        ['host-key-algorithms', '', None],
        ['known-hosts', '', None, 'File to check for host keys'],
        ['user-authentications', '', None, 'Types of user authentications to use.'],
        ['logfile', '', None, 'File to log to, or - for stdout'],
    ]

    optFlags = [
        ['version', 'V', 'Display version number only.'],
        ['compress', 'C', 'Enable compression.'],
        ['log', 'v', 'Enable logging (defaults to stderr)'],
        ['nox11', 'x', 'Disable X11 connection forwarding (default)'],
        ['agent', 'A', 'Enable authentication agent forwarding'],
        ['noagent', 'a', 'Disable authentication agent forwarding (default)'],
        ['reconnect', 'r', 'Reconnect to the server if the connection is lost.'],
    ]

    compData = usage.Completions(
        mutuallyExclusive=[("agent", "noagent")],
        optActions={
            "user": usage.CompleteUsernames(),
            "ciphers": usage.CompleteMultiList(
                SSHCiphers.cipherMap.keys(),
                descr='ciphers to choose from'),
            "macs": usage.CompleteMultiList(
                SSHCiphers.macMap.keys(),
                descr='macs to choose from'),
            "host-key-algorithms": usage.CompleteMultiList(
                SSHClientTransport.supportedPublicKeys,
                descr='host key algorithms to choose from'),
            "user-authentications": usage.CompleteMultiList(
                [],
                descr='user authentication types' ),
            },
        extraActions=[usage.CompleteUserAtHost(),
                      usage.Completer(descr="command"),
                      usage.Completer(descr='argument',
                                      repeat=True)]
        )

    def __init__(self, *args, **kw):
        usage.Options.__init__(self, *args, **kw)
        self.identitys: List[str] = []
        self.conns: Optional[str] = None

    def opt_identity(self, i: str):
        """Identity for public-key authentication"""
        self.identitys.append(i)

    def opt_ciphers(self, ciphers: str):
        "Select encryption algorithms"
        ciphers = ciphers.split(',')
        valid_ciphers = set(SSHCiphers.cipherMap.keys())
        for cipher in ciphers:
            if cipher not in valid_ciphers:
                raise ValueError(f"Unknown cipher type '{cipher}'")
        self['ciphers'] = ciphers

    def opt_macs(self, macs: str):
        "Specify MAC algorithms"
        macs = macs.split(',')
        valid_macs = set(SSHCiphers.macMap.keys())
        for mac in macs:
            if mac not in valid_macs:
                raise ValueError(f"Unknown mac type '{mac}'")
        self['macs'] = macs

    def opt_host_key_algorithms(self, hkas: str):
        "Select host key algorithms"
        hkas = hkas.split(',')
        valid_hkas = set(SSHClientTransport.supportedPublicKeys)
        for hka in hkas:
            if hka not in valid_hkas:
                raise ValueError(f"Unknown host key type '{hka}'")
        self['host-key-algorithms'] = hkas

    def opt_user_authentications(self, uas: str):
        "Choose how to authenticate to the remote server"
        self['user-authentications'] = uas.split(',')

    def opt_compress(self):
        "Enable compression"
        self.enableCompression = 1
        SSHClientTransport.supportedCompressions[0:1] = ['zlib']

    def parse_option(self, option: str):
        """
        Parse an OpenSSH option.
        """
        pass

