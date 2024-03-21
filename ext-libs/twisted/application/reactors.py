# -*- test-case-name: twisted.test.test_application -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Plugin-based system for enumerating available reactors and installing one of
them.
"""

from zope.interface import Interface, Attribute, implements
from typing import List, Any, TypeVar, Optional
from twisted.plugin import IPlugin, getPlugins
from twisted.python.reflect import namedAny
from twisted.python.util import sibling


T = TypeVar('T')


class IReactorInstaller(Interface):
    """
    Definition of a reactor which can probably be installed.
    """
    shortName: str
    description: str

    def install(self) -> None:
        """
        Install this reactor.
        """


class NoSuchReactor(KeyError):
    """
    Raised when an attempt is made to install a reactor which cannot be found.
    """


class Reactor(object):
    """
    @ivar moduleName: The fully-qualified Python name of the module of which
    the install callable is an attribute.
    """
    implements(IPlugin, IReactorInstaller)

    def __init__(self, shortName: str, moduleName: str, description: str):
        self.shortName = shortName
        self.moduleName = moduleName
        self.description = description

    def install(self) -> None:
        try:
            reactorModule = sibling(self.moduleName)
            namedAny(reactorModule).install()
        except Exception as e:
            raise Exception(f"Failed to install reactor {self.shortName}: {e}")


def getReactorTypes() -> List[IReactorInstaller]:
    """
    Return an iterator of L{IReactorInstaller} plugins.
    """
    return getPlugins(IReactorInstaller)


def installReactor(shortName: str) -> None:
    """
    Install the reactor with the given C{shortName} attribute.

    @raise NoSuchReactor: If no reactor is found with a matching C{shortName}.

    @raise: anything that the specified reactor can raise when installed.
    """
    for installer in getReactorTypes():
        if installer.shortName == shortName:
            try:
                installer.install()
                return
            except Exception as e:
                raise Exception(f"Failed to install reactor {shortName}: {e}")
    raise NoSuchReactor(shortName)


__all__ = [
    'IReactorInstaller', 'NoSuchReactor', 'Reactor', 'getReactorTypes',
    'installReactor'
]
