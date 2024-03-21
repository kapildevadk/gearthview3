# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.application} and its interaction with
L{twisted.persisted.sob}.
"""

import os
import pickle
import copy
import unittest
from unittest.mock import patch
from io import StringIO
from typing import Any, Callable, Dict, List, Optional

import twisted.trial
from twisted.application import service, internet, app
from twisted.persisted import sob
from twisted.python import usage
from twisted.internet import interfaces, defer
from twisted.protocols import wire, basic
from twisted.internet import protocol, reactor
from twisted.application import reactors
from twisted.test.proto_helpers import MemoryReactor


class Dummy:
    processName = None


class TestService(unittest.TestCase):

    def test_service_name(self) -> None:
        s = service.Service()
        s.setName("hello")
        self.assertEqual(s.name, "hello")

    def test_service_parent(self) -> None:
        s = service.Service()
        p = service.MultiService()
        s.setServiceParent(p)
        self.assertEqual(list(p), [s])
        self.assertEqual(s.parent, p)

    def test_application_as_parent(self) -> None:
        s = service.Service()
        p = service.Application("")
        s.setServiceParent(p)
        self.assertEqual(list(service.IServiceCollection(p)), [s])
        self.assertEqual(s.parent, service.IServiceCollection(p))

    def test_named_child(self) -> None:
        s = service.Service()
        p = service.MultiService()
        s.setName("hello")
        s.setServiceParent(p)
        self.assertEqual(list(p), [s])
        self.assertEqual(s.parent, p)
        self.assertEqual(p.getServiceNamed("hello"), s)

    def test_doubly_named_child(self) -> None:
        s = service.Service()
        p = service.MultiService()
        s.setName("hello")
        s.setServiceParent(p)
        with self.assertRaises(RuntimeError):
            s.setName("lala")

    def test_duplicate_named_child(self) -> None:
        s = service.Service()
        p = service.MultiService()
        s.setName("hello")
        s.setServiceParent(p)
        s1 = service.Service()
        s1.setName("hello")
        with self.assertRaises(RuntimeError):
            s1.setServiceParent(p)

    def test_disowning(self) -> None:
        s = service.Service()
        p = service.MultiService()
        s.setServiceParent(p)
        self.assertEqual(list(p), [s])
        self.assertEqual(s.parent, p)
        s.disownServiceParent()
        self.assertEqual(list(p), [])
        self.assertEqual(s.parent, None)

    def test_running(self) -> None:
        s = service.Service()
        self.assertFalse(s.running)
        s.startService()
        self.assertTrue(s.running)
        s.stopService()
        self.assertFalse(s.running)

    def test_running_children_1(self) -> None:
        s = service.Service()
        p = service.MultiService()
        s.setServiceParent(p)
        self.assertFalse(s.running)
        self.assertFalse(p.running)
        p.startService()
        self.assertTrue(s.running)
        self.assertTrue(p.running)
        p.stopService()
        self.assertFalse(s.running)
        self.assertFalse(p.running)

    def test_running_children_2(self) -> None:
        s = service.Service()
        t = service.Service()
        t.stopService = lambda: None
        t.startService = lambda: None
        p = service.MultiService()
        s.setServiceParent(p)
        t.setServiceParent(p)
        p.startService()
        p.stopService()

    def test_adding_into_running(self) -> None:
        p = service.MultiService()
        p.startService()
        s = service.Service()
        self.assertFalse(s.running)
        s.setServiceParent(p)
        self.assertTrue(s.running)
        s.disownServiceParent()
        self.assertFalse(s.running)

    def test_privileged(self) -> None:
        s = service.Service()
        def pss():
            s.privilegedStarted = 
