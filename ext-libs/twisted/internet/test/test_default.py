# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.internet.default}.
"""

from __future__ import division, absolute_import

import asyncio
import select
from typing import Callable, TypeVar, Any
from twisted.trial.asyncio import AsyncioTestCase
from twisted.python.runtime import Platform
from twisted.internet import default, interfaces
from twisted.internet.interfaces import IReactorCore
from twisted.internet.test.test_main import NoReactor
from zope.interface import getUtility

T = TypeVar('T')

unix = Platform('posix', 'other')
linux = Platform('posix', 'linux2')
windows = Platform('nt', 'win32')
osx = Platform('posix', 'darwin')


class ReactorTests(AsyncioTestCase):
    """
    Tests for the cases of L{twisted.internet.default._getInstallFunction}
    in which it picks the poll(2) or epoll(7)-based reactors.
    """

    def assertIsPoll(self, install: Callable[[], T]) -> None:
        """
        Assert the given function will install the poll() reactor, or select()
        if poll() is unavailable.
        """
        if select.select.available_on_posix():
            self.assertIsInstance(install(), interfaces.IPollReactor)
        else:
            self.assertIsInstance(install(), interfaces.ISelectReactor)

    async def test_unix(self) -> None:
        """
        L{_getInstallFunction} chooses the poll reactor on arbitrary Unix
        platforms, falling back to select(2) if it is unavailable.
        """
        install = _getInstallFunction(unix)
        self.assertIsPoll(install)

    async def test_linux(self) -> None:
        """
        L{_getInstallFunction} chooses the epoll reactor on Linux, or poll if
        epoll is unavailable.
        """
        install = _getInstallFunction(linux)
        try:
            epollreactor = getUtility(IReactorCore, 'epoll')
        except ImportError:
            self.assertIsPoll(install)
        else:
            self.assertIsInstance(install(), type(epollreactor))


class SelectReactorTests(AsyncioTestCase):
    """
    Tests for the cases of L{twisted.internet.default._getInstallFunction}
    in which it picks the select(2)-based reactor.
    """
    async def test_osx(self) -> None:
        """
        L{_getInstallFunction} chooses the select reactor on OS X.
        """
        install = _getInstallFunction(osx)
        self.assertIsInstance(install(), interfaces.ISelectReactor)

    async def test_windows(self) -> None:
        """
        L{_getInstallFunction} chooses the select reactor on Windows.
        """
        install = _getInstallFunction(windows)
        self.assertIsInstance(install(), interfaces.ISelectReactor)


class InstallationTests(AsyncioTestCase):
    """
    Tests for actual installation of the reactor.
    """

    async def test_install(self) -> None:
        """
        L{install} installs a reactor.
        """
        with NoReactor():
            install()
            self.assertIn("twisted.internet.reactor", dir(sys.modules))

    async def test_reactor(self) -> None:
        """
        Importing L{twisted.internet.reactor} installs the default reactor if
        none is installed.
        """
        installed = []

        def installer() -> None:
            installed.append(True)
            return install()

        self.patch(default, "install", installer)

        with NoReactor():
            from twisted.internet import reactor
            self.assertTrue(interfaces.IReactorCore.providedBy(reactor))
            self.assertEqual(installed, [True])

