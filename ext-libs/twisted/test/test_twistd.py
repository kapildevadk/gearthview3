import os
import sys
import signal
import errno
import StringIO
import tempfile
import unittest.mock as mock
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.case import TestCase
from twisted.trial import unittest
from twisted.test.test_process import MockOS
from twisted.internet import defer, interfaces, reactor, task
from twisted.python import log, components, components as cp, usage, components, version
from twisted.python.log import ILogObserver
from twisted.python.usage import Options
from twisted.python.components import registerAdapter
from twisted.python.filepath import FilePath
from twisted.python.reflect import qual
from twisted.python.runtime import platformType
from twisted.application.service import IServiceMaker
from twisted.application import service, app, reactors
from twisted.scripts import twistd
from twisted.python.usage import UsageError
from twisted.python.log import ILogObserver
from twisted.python.versions import Version
from twisted.python.components import Componentized
from twisted.internet.defer import Deferred
from twisted.internet.interfaces import IReactorDaemonize
from twisted.python.fakepwd import UserDatabase
from twisted.scripts._twistd_unix import UnixApplicationRunner
from twisted.scripts._twistd_unix import UnixAppLogger
from twisted.python.util import sibpath
from twisted.python.modules import getModule
from twisted.python.compat import nativeString
from twisted.python.dist import Distribution
from twisted.python.util import runWithWarningsSuppressed
from twisted.python.failure import Failure
from twisted.python.direct import installWsgiApplication
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.web.static import File
from twisted.web.resource import Resource
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.verify import verifyObject


class TestCase(unittest.TestCase):
    def mktemp(self) -> str:
        return tempfile.mktemp()


@implementer(ILogObserver)
class CrippledAppLogger(app.AppLogger):
    def start(self, application: Any) -> None:
        pass


class CrippledApplicationRunner(twistd._SomeApplicationRunner):
    loggerFactory = CrippledAppLogger

    def preApplication(self) -> None:
        pass

    def postApplication(self) -> None:
        pass


class ServerOptionsTest(TestCase):
    def test_subCommands(self) -> None:
        class FakePlugin(object):
            def __init__(self, name: str) -> None:
                self.tapname = name
                self._options = f'options for {name}'
                self.description = f'description of {name}'

            def options(self) -> str:
                return self._options

        apple = FakePlugin('apple')
        banana = FakePlugin('banana')
        coconut = FakePlugin('coconut')
        donut = FakePlugin('donut')

        def getPlugins(interface: Interface) -> List[Any]:
            self.assertEqual(interface, IServiceMaker)
            yield coconut
            yield banana
            yield donut
            yield apple

        config = twistd.ServerOptions()
        self.assertEqual(config._getPlugins, plugin.getPlugins)
        config._getPlugins = getPlugins

        subCommands = config.subCommands
        expectedOrder = [apple, banana, coconut, donut]

        for subCommand, expectedCommand in zip(subCommands, expectedOrder):
            name, shortcut, parserClass, documentation = subCommand
            self.assertEqual(name, expectedCommand.tapname)
            self.assertEqual(shortcut, None)
            self.assertEqual(parserClass(), expectedCommand._options)
            self.assertEqual(documentation, expectedCommand.description)

    def test_sortedReactorHelp(self) -> None:
        class FakeReactorInstaller(object):
            def __init__(self, name: str) -> None:
                self.shortName = f'name of {name}'
                self.description = f'description of {name}'

        apple = FakeReactorInstaller('apple')
        banana = FakeReactorInstaller('banana')
        coconut = FakeReactorInstaller('coconut')
        donut = FakeReactorInstaller('donut')

        def getReactorTypes() -> List[Any]:
            yield coconut
            yield banana
            yield donut
            yield apple

        config = twistd.ServerOptions()
        self.assertEqual(config._getReactorTypes, reactors.getReactorTypes)
        config._getReactorTypes = getReactorTypes
        config.messageOutput = StringIO.StringIO()

        self.assertRaises(task.ReactorBuiltError, config.parseOptions, ['--help-reactors'])
        helpOutput = config.messageOutput.getvalue()
        indexes = []
        for reactor in apple, banana, coconut, donut:
            def getIndex(s: str) -> None:
                self.assertIn(s, helpOutput)
                indexes.append(help
