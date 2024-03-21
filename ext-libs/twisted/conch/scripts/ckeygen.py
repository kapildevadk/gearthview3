# -*- test-case-name: twisted.conch.test.test_ckeygen -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Implementation module for the `ckeygen` command.
"""

import sys
import os
import getpass
import socket
import termios
import Crypto.PublicKey
import random
import keyczar
from twisted.conch.ssh import keys
from twisted.python import filepath, log, usage, randbytes
from twisted.python.usage import Options, Completions


class GeneralOptions(Options):
    synopsis = """Usage:    ckeygen [options]
 """

    longdesc = "ckeygen manipulates public/private keys in various ways."

    optParameters = [
        ['bits', 'b', 1024, 'Number of bits in the key to create.'],
        ['filename', 'f', None, 'Filename of the key file.'],
        ['type', 't', None, 'Specify type of key to create.'],
        ['comment', 'C', None, 'Provide new comment.'],
        ['newpass', 'N', None, 'Provide new passphrase.'],
        ['pass', 'P', None, 'Provide old passphrase']]

    optFlags = [
        ['fingerprint', 'l', 'Show fingerprint of key file.'],
        ['changepass', 'p', 'Change passphrase of private key file.'],
        ['quiet', 'q', 'Quiet.'],
        ['showpub', 'y', 'Read private key file and print public key.']]

    compData = Completions(
        optActions={"type": Completions.CompleteList(["rsa", "dsa"])})


def run():
    options = GeneralOptions()
    try:
        options.parseOptions(sys.argv[1:])
    except usage.UsageError, u:
        print 'ERROR: %s' % u
        options.opt_help()
        sys.exit(1)
    log.discardLogs()
    log.deferr = handleError  # HACK
    if options['type']:
        if options['type'] == 'rsa':
            generateRSAkey(options)
        elif options['type'] == 'dsa':
            generateDSAkey(options)
        else:
            sys.exit('Key type was %s, must be one of: rsa, dsa' % options['type'])
    elif options['fingerprint']:
        printFingerprint(options)
    elif options['changepass']:
        changePassPhrase(options)
    elif options['showpub']:
        displayPublicKey(options)
    else:
        options.opt_help()
        sys.exit(1)


def handleError():
    from twisted.python import failure
    global exitStatus
    exitStatus = 2
    log.err(failure.Failure())
    # reactor.stop()  # Uncomment if you're using Twisted
    raise


def generateRSAkey(options):
    print('Generating public/private rsa key pair.')
    key = Crypto.PublicKey.RSA.generate(int(options['bits']), random.SystemRandom())
    _saveKey(key, options)


def generateDSAkey(options):
    print('Generating public/private dsa key pair.')
    key = Crypto.PublicKey.DSA.generate(int(options['bits']), random.SystemRandom())
    _saveKey(key, options)


def printFingerprint(options):
    if not options['filename']:
        filename = os.path.expanduser('~/.ssh/id_rsa')
        options['filename'] = input('Enter file in which the key is (%s): ' % filename) or filename
    if os.path.exists(options['filename'] + '.pub'):
        options['filename'] += '.pub'
    try:
        with open(options['filename'], 'rb') as f:
            key_str = f.read()
        key = keyczar.Key.Read(key_str)
        print('%s %s %s' % (
            key.size() + 1,
            key.Fingerprint(),
            os.path.basename(options['filename'])))
    except Exception as e:
        print('bad key')


def changePassPhrase(options):
    if not options['filename']:
        filename = os.path.expanduser('~/.ssh/id_rsa')
        options['filename'] = input('Enter file in which the key is (%s): ' % filename) or filename
    try:
        with open(options['filename'], 'rb') as f:
            key_str = f.read()
        key = keyczar.Key.Read(key_str)
    except keyczar.BadKeyError as e:
        if e.args[0] != 'encrypted key with no passphrase':
            raise
        else:
            if not options['pass']:
                options['pass'] = getpass.getpass('Enter old passphrase: ')
            key = keyczar.Key.Read(key_str, password=options['pass'])
    if not options['newpass']:
        while 1:
            p1 = getpass.getpass('Enter new passphrase (empty for no passphrase): ')
            p2 = getpass.getpass('Enter same passphrase again: ')
            if p1 == p2:
                break
            print('Passphrases do not match.  Try again.')
        options['newpass'] = p1
    with open(options['filename'], 'wb') as f:
        f.write(key.SerializeToString(password=options['newpass']))
    print('Your identification has been saved with the new passphrase.')


def displayPublicKey(options):
    if not options['filename']:
        filename = os.path.expanduser('~/.ssh/id_rsa')
        options['filename'] = input('Enter file in which the key is (%s): ' % filename) or filename
    try:
        with open(options['filename'], 'rb') as f:
            key_str = f.
