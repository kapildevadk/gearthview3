# -*- test-case-name: twisted.test.test_pb -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Perspective Broker

This module provides the Perspective Broker, a broker for proxies for and
copies of objects. It provides a translucent interface layer to those proxies.

The protocol is not opaque, because it provides objects which represent the
remote proxies and require no context (server references, IDs) to operate on.

It is not transparent because it does not attempt to make remote objects behave
identically, or even similarly, to local objects. Method calls are invoked
asynchronously, and specific rules are applied when serializing arguments.

To get started, begin with `PBClientFactory` and `PBServerFactory`.

@author: Glyph Lefkowitz
"""

import random
import types
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import zope.interface
from twisted.python import log
from twisted.python.failure import Failure
from twisted.python.hashlib import md5
from twisted.internet import defer
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.cred.portal import Portal
from twisted.cred.credentials import IAnonymous
from twisted.cred.credentials import ICredentials
from twisted.cred.credentials import IUsernameHashedPassword
from twisted.cred.checkers import ICredentialsChecker
from twisted.persisted import styles
from twisted.python.components import registerAdapter
from twisted.spread.interfaces import IJellyable
from twisted.spread.interfaces import IUnjellyable
from twisted.spread.jelly import jelly
from twisted.spread.jelly import unjelly
from twisted.spread.jelly import globalSecurity
from twisted.spread import banana
from twisted.spread.flavors import Serializable
from twisted.spread.flavors import Referenceable
from twisted.spread.flavors import NoSuchMethod
from twisted.spread.flavors import Root
from twisted.spread.flavors import IPBRoot
from twisted.spread.flavors import ViewPoint
from twisted.spread.flavors import Viewable
from twisted.spread.flavors import Copyable
from twisted.spread.flavors import Jellyable
from twisted.spread.flavors import Cacheable
from twisted.spread.flavors import RemoteCopy
from twisted.spread.flavors import RemoteCache
from twisted.spread.flavors import RemoteCacheObserver
from twisted.spread.flavors import copyTags
from twisted.spread.flavors import setUnjellyableForClass
from twisted.spread.flavors import setUnjellyableFactoryForClass
from twisted.spread.flavors import setUnjellyableForClassTree
from twisted.spread.flavors import setCopierForClass
from twisted.spread.flavors import setFactoryForClass
from twisted.spread.flavors import setCopierForClassTree

MAX_BROKER_REFS = 1024
portno = 
