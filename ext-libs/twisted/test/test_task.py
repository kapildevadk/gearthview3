import asyncio
import unittest
from unittest.mock import patch, AsyncMock
from typing import Any, Callable, Dict, List, Optional

# Be compatible with any jerks who used our private stuff
from twisted.internet.task import Clock


class TestableLoopingCall(Clock.LoopingCall):
    def __init__(self, clock: Clock, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.clock = clock


class TestException(Exception):
    pass


class ClockTestCase(unittest.TestCase):
    """
    Test the non-wallclock based clock implementation.
    """

    @patch('twisted.internet.reactor', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.seconds', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.callLater', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.advance', new_callable=AsyncMock)
    async def test_seconds(self, mock_advance, mock_call_later, mock_seconds, mock_reactor):
        """
        Test that the C{seconds} method of the fake clock returns fake time.
        """
        clock = Clock()
        self.assertEqual(await clock.seconds(), 0)

        mock_seconds.return_value = 10
        self.assertEqual(await clock.seconds(), 10)

    @patch('twisted.internet.reactor', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.callLater', new_callable=AsyncMock)
    async def test_call_later(self, mock_call_later, mock_reactor):
        """
        Test that calls can be scheduled for later with the fake clock and
        hands back an L{IDelayedCall}.
        """
        clock = Clock()
        call = clock.callLater(1, lambda a, b: None, 1, b=2)
        self.assertTrue(await call.called)
        self.assertEqual(call.getTime(), 1)
        self.assertTrue(call.active())

    @patch('twisted.internet.reactor', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.callLater', new_callable=AsyncMock)
    async def test_call_later_cancelled(self, mock_call_later, mock_reactor):
        """
        Test that calls can be cancelled.
        """
        clock = Clock()
        call = clock.callLater(1, lambda a, b: None, 1, b=2)
        call.cancel()
        self.assertFalse(call.active())

    @patch('twisted.internet.reactor', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.callLater', new_callable=AsyncMock)
    async def test_call_later_ordering(self, mock_call_later, mock_reactor):
        """
        Test that the DelayedCall returned is not one previously
        created.
        """
        clock = Clock()
        call1 = clock.callLater(10, lambda a, b: None, 1, b=2)
        call2 = clock.callLater(1, lambda a, b: None, 3, b=4)
        self.assertIsNot(call1, call2)

    @patch('twisted.internet.reactor', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.advance', new_callable=AsyncMock)
    async def test_advance(self, mock_advance, mock_reactor):
        """
        Test that advancing the clock will fire some calls.
        """
        events = []
        clock = Clock()
        call = clock.callLater(2, lambda: events.append(None))
        await mock_advance(1)
        self.assertEqual(events, [])
        await mock_advance(1)
        self.assertEqual(events, [None])
        self.assertFalse(call.active())

    @patch('twisted.internet.reactor', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.callLater', new_callable=AsyncMock)
    async def test_advance_cancel(self, mock_call_later, mock_reactor):
        """
        Test attemping to cancel the call in a callback.

        AlreadyCalled should be raised, not for example a ValueError from
        removing the call from Clock.calls. This requires call.called to be
        set before the callback is called.
        """
        clock = Clock()

        def cb():
            with self.assertRaises(clock.AlreadyCalled):
                call.cancel()

        call = clock.callLater(1, cb)
        await mock_advance(1)

    @patch('twisted.internet.reactor', new_callable=AsyncMock)
    @patch('twisted.internet.task.Clock.callLater', new_callable=AsyncMock)
    async def test_call_later_delayed(self, mock_call_later, mock
