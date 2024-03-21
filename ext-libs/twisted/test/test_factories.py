# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test code for basic Factory classes.
"""

import pickle
from unittest.mock import Mock, patch
from unittest import TestCase, skip

from twisted.trial.unittest import TestCase
from twisted.internet.task import Clock
from twisted.internet.protocol import ReconnectingClientFactory, Protocol


class FakeConnector:
    """
    A fake connector class, to be used to mock connections failed or lost.
    """

    def stopConnecting(self):
        pass

    def connect(self):
        pass


class ReconnectingFactoryTestCase(TestCase):
    """
    Tests for L{ReconnectingClientFactory}.
    """

    def test_stopTryingWhenConnected(self, protocol_factory=Protocol):
        """
        If a L{ReconnectingClientFactory} has C{stopTrying} called while it is
        connected, it does not subsequently attempt to reconnect if the
        connection is later lost.
        """
        c = ReconnectingClientFactory()
        c.protocol = protocol_factory
        # Let's pretend we've connected:
        c.buildProtocol(None)
        # Now we stop trying, then disconnect:
        c.stopTrying()
        c.clientConnectionLost(FakeConnector(), None)
        self.assertFalse(c.continueTrying)

    @skip("Test requires a reactor")
    def test_stopTryingDoesNotReconnect(self):
        """
        Calling stopTrying on a L{ReconnectingClientFactory} doesn't attempt a
        retry on any active connector.
        """
        with patch('twisted.internet.task.Clock') as mock_clock:
            f = ReconnectingClientFactory()
            f.clock = mock_clock

            # simulate an active connection - stopConnecting on this connector should
            # be triggered when we call stopTrying
            f.connector = Mock()
            f.connector.attemptedRetry = False
            f.stopTrying()

            # make sure we never attempted to retry
            self.assertFalse(f.connector.attemptedRetry)
            self.assertFalse(mock_clock.getDelayedCalls())

    def test_serializeUnused(self):
        """
        A L{ReconnectingClientFactory} which hasn't been used for anything
        can be pickled and unpickled and end up with the same state.
        """
        original = ReconnectingClientFactory()
        reconstituted = pickle.loads(pickle.dumps(original))
        self.assertEqual(original.__dict__, reconstituted.__dict__)

    def test_serializeWithClock(self):
        """
        The clock attribute of L{ReconnectingClientFactory} is not serialized,
        and the restored value sets it to the default value, the reactor.
        """
        clock = Clock()
        original = ReconnectingClientFactory()
        original.clock = clock
        reconstituted = pickle.loads(pickle.dumps(original))
        self.assertIsNone(reconstituted.clock)

    def test_deserializationResetsParameters(self):
        """
        A L{ReconnectingClientFactory} which is unpickled does not have an
        L{IConnector} and has its reconnecting timing parameters reset to their
        initial values.
        """
        factory = ReconnectingClientFactory()
        factory.clientConnectionFailed(FakeConnector(), None)
        self.addCleanup(factory.stopTrying)

        serialized = pickle.dumps(factory)
        unserialized = pickle.loads(serialized)
        self.assertIsNone(unserialized.connector)
        self.assertIsNone(unserialized._callID)
        self.assertEqual(unserialized.retries, 0)
        self.assertEqual(unserialized.delay, factory.initialDelay)
        self.assertTrue(unserialized.continueTrying)

    def test_parametrizedClock(self):
        """
        The clock used by L{ReconnectingClientFactory} can be parametrized, so
        that one can cleanly test reconnections.
        """
        clock = Clock()
        factory = ReconnectingClientFactory()
        factory.clock = clock

        factory.clientConnectionLost(FakeConnector(), None)
        self.assertEqual(len(clock.calls), 1)
