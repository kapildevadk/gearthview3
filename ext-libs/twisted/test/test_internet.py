# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for lots of functionality provided by L{twisted.internet}.
"""

import os
import sys
import time
from twisted.python.compat import _PY3
from twisted.trial import unittest
from twisted.internet import reactor, protocol, error, abstract, defer
from twisted.internet import interfaces, base, ssl, endpoints
from twisted.python import runtime
if not _PY3:
    from twisted.python import util

class ThreePhaseEventTests(unittest.TestCase):
    """
    Tests for the private implementation helpers for system event triggers.
    """
    def setUp(self):
        """
        Create a trigger, an argument, and an event to be used by tests.
        """
        self.trigger = lambda x: None
        self.arg = object()
        self.event = base._ThreePhaseEvent()

    def test_addInvalidPhase(self):
        """
        L{_ThreePhaseEvent.addTrigger} should raise L{KeyError} when called
        with an invalid phase.
        """
        self.assertRaises(
            KeyError,
            self.event.addTrigger, 'xxx', self.trigger, self.arg)

    def test_addBeforeTrigger(self):
        """
        L{_ThreePhaseEvent.addTrigger} should accept C{'before'} as a phase, a
        callable, and some arguments and add the callable with the arguments to
        the before list.
        """
        self.event.addTrigger('before', self.trigger, self.arg)
        self.assertEqual(
            self.event.before,
            [(self.trigger, (self.arg,), {})])

    def test_addDuringTrigger(self):
        """
        L{_ThreePhaseEvent.addTrigger} should accept C{'during'} as a phase, a
        callable, and some arguments and add the callable with the arguments to
        the during list.
        """
        self.event.addTrigger('during', self.trigger, self.arg)
        self.assertEqual(
            self.event.during,
            [(self.trigger, (self.arg,), {})])

    def test_addAfterTrigger(self):
        """
        L{_ThreePhaseEvent.addTrigger} should accept C{'after'} as a phase, a
        callable, and some arguments and add the callable with the arguments to
        the after list.
        """
        self.event.addTrigger('after', self.trigger, self.arg)
        self.assertEqual(
            self.event.after,
            [(self.trigger, (self.arg,), {})])

    def test_removeTrigger(self):
        """
        L{_ThreePhaseEvent.removeTrigger} should accept an opaque object
        previously returned by L{_ThreePhaseEvent.addTrigger} and remove the
        associated trigger.
        """
        handle = self.event.addTrigger('before', self.trigger, self.arg)
        self.event.removeTrigger(handle)
        self.assertEqual(self.event.before, [])

    def test_removeNonexistentTrigger(self):
        """
        L{_ThreePhaseEvent.removeTrigger} should raise L{ValueError} when given
        an object not previously returned by L{_ThreePhaseEvent.addTrigger}.
        """
        self.assertRaises(ValueError, self.event.removeTrigger, object())

    def test_removeRemovedTrigger(self):
        """
        L{_ThreePhaseEvent.removeTrigger} should raise L{ValueError} the second
        time it is called with an object returned by
        L{_ThreePhaseEvent.addTrigger}.
        """
        handle = self.event.addTrigger('before', self.trigger, self.arg)
        self.event.removeTrigger(handle)
        self.assertRaises(ValueError, self.event.removeTrigger, handle)

    def test_removeAlmostValidTrigger(self):
        """
        L{_ThreePhaseEvent.removeTrigger} should raise L{ValueError} if it is
        given a trigger handle which resembles a valid trigger handle aside
        from its phase being incorrect.
        """
        self.assertRaises(
            KeyError,
            self.event.removeTrigger, ('xxx', self.trigger, (self.arg,), {}))

    def test_fireEvent(self):
        """
        L{_ThreePhaseEvent.fireEvent} should call I{before}, I{during}, and
        I{after} phase triggers in that order.
        """
        events = []
        self.event.addTrigger('after', events.append, ('first', 'after'))
        self.event.addTrigger('during', events.append, ('first', 'during'))
        self.event.addTrigger('before', events.append, ('first', 'before'))
        self.event.addTrigger('before', events.append, ('second', 'before'))
        self.event.addTrigger('during', events.append, ('second', 'during'))
        self.event.addTrigger('after', events.append, ('second', 'after'))

        self.assertEqual(events, [])
        self.event.fireEvent()
        self.assertEqual(events,
                         [('first', 'before'), ('second', 'before'),
                          ('first', 'during'), ('second', 'during'),
                          ('first', 'after'), ('second', 'after')])

    def test_asynchronousBefore(self):
        """
        L{_ThreePhaseEvent.fireEvent} should wait for any L{Deferred} returned
        by a I{before} phase trigger before proceeding to I{during} events.
        """
        events = []
        beforeResult = defer.Deferred()
        self.event.addTrigger('before', lambda: beforeResult)
        self.event.addTrigger('during', events.append, 'during')
        self.event.addTrigger('after', events.append, 'after')

        self.assertEqual(events, [])
        self.event.fireEvent()
        self.assertEqual(events, [])
        beforeResult.callback(None)
        self.
