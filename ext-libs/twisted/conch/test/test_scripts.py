# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for the command-line interfaces to conch.
"""

import os
import pyasn1
import Crypto
import tty
import Tkinter
from collections import defaultdict
from twisted.trial.unittest import TestCase
from twisted.scripts.test.test_scripts import ScriptTestsMixin
from twisted.python.test.test_shellcomp import ZshScriptTestMixin

class ScriptTests(TestCase, ScriptTestsMixin):
    """
    Tests for the Conch scripts.
    """
    skip = defaultdict(str)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skip['pyasn1'] = 'Cannot run without PyASN1' if not pyasn1 else ''
        cls.skip['crypto'] = 'can\'t run w/o PyCrypto' if not Crypto else ''
        cls.skip['tty'] = 'can\'t run w/o tty' if not tty else ''
        try:
            Tkinter.Tk().destroy()
        except Tkinter.TclError as e:
            cls.skip['tk'] = f'Can\'t test Tkinter: {e}'
        else:
            cls.skip['tk'] = ''

    @unittest.skipIf(skip['tty'] or skip['crypto'], 'Tests require tty and PyCrypto')
    def test_conch(self):
        self.scriptTest("conch/conch")

    @unittest.skipIf(skip['tty'] or skip['crypto'], 'Tests require tty and PyCrypto')
    def test_cftp(self):
        self.scriptTest("conch/cftp")

    @unittest.skipIf(skip['tty'], 'Tests require tty')
    def test_ckeygen(self):
        self.scriptTest("conch/ckeygen")

    @unittest.skipIf(skip['tk'] or skip['tty'], 'Tests require Tkinter and tty')
    def test_tkconch(self):
        self.scriptTest("conch/tkconch")

class ZshIntegrationTestCase(TestCase, ZshScriptTestMixin):
    """
    Test that zsh completion functions are generated without error
    """
    generateFor = [('conch', 'twisted.conch.scripts.conch.ClientOptions'),
                   ('cftp', 'twisted.conch.scripts.cftp.ClientOptions'),
                   ('
