# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for returning Deferreds from a TestCase.
"""

import unittest as pyunit
import pytest
from unittest.mock import patch
from twisted.internet import defer, reactor
from twisted.trial import unittest, reporter
from twisted.trial import util
from twisted.trial.test import detests

pytestmark = pytest.mark.usefixtures("event_loop")


class TestSetUp(unittest.TestCase):
    """
    Tests for the DeferredSetUpOK, DeferredSetUpFail, DeferredSetUpCallbackFail,
    DeferredSetUpError, and DeferredSetUpSkip classes.
    """

    @staticmethod
    def _load_suite(klass):
        loader = pyunit.TestLoader()
        r = reporter.TestResult()
        s = loader.loadTestsFromTestCase(klass)
        return r, s

    def test_success(self, result: reporter.TestResult, suite: pyunit.TestSuite):
        """
        Test that the DeferredSetUpOK test case runs successfully.
        """
        result, suite = self._load_suite(detests.DeferredSetUpOK)
        suite.run(result)
        assert result.wasSuccessful()
        assert result.testsRun == 1

    def test_fail(self, result: reporter.TestResult, suite: pyunit.TestSuite):
        """
        Test that the DeferredSetUpFail test case fails.
        """
        result, suite = self._load_suite(detests.DeferredSetUpFail)
        suite.run(result)
        assert not result.wasSuccessful()
        assert result.testsRun == 1
        assert len(result.failures) == 0
        assert len(result.errors) == 1

    def test_callback_fail(
        self, result: reporter.TestResult, suite: pyunit.TestSuite
    ):
        """
        Test that the DeferredSetUpCallbackFail test case fails.
        """
        result, suite = self._load_suite(detests.DeferredSetUpCallbackFail)
        suite.run(result)
        assert not result.wasSuccessful()
        assert result.testsRun == 1
        assert len(result.failures) == 0
        assert len(result.errors) == 1

    def test_error(self, result: reporter.TestResult, suite: pyunit.TestSuite):
        """
        Test that the DeferredSetUpError test case fails.
        """
        result, suite = self._load_suite(detests.DeferredSetUpError)
        suite.run(result)
        assert not result.wasSuccessful()
        assert result.testsRun == 1
        assert len(result.failures) == 0
        assert len(result.errors) == 1

    def test_skip(self, result: reporter.TestResult, suite: pyunit.TestSuite):
        """
        Test that the DeferredSetUpSkip test case is skipped.
        """
        result, suite = self._load_suite(detests.DeferredSetUpSkip)
        suite.run(result)
        assert result.wasSuccessful()
        assert result.testsRun == 1
        assert len(result.failures) == 0
        assert len(result.errors) == 0
        assert len(result.skips) == 1


@pytest.mark.asyncio
async def test_never_fire(event_loop):
    """
    Test that the DeferredSetUpNeverFire test case fails.
    """
    from twisted.internet import reactor

    util.DEFAULT_TIMEOUT_DURATION = 0.1

    @defer.inlineCallbacks
    def test():
        d = defer.Deferred()
        yield d

    result = reporter.TestResult()
    detests.DeferredSetUpNeverFire(test).run(result)
    await event_loop.runUntilComplete(result.deferred)
    assert not result.wasSuccessful()
    assert result.testsRun == 1
    assert len(result.failures) == 0
    assert len(result.errors) == 1
    assert isinstance(result.errors[0][1], defer.TimeoutError)

    util.DEFAULT_TIMEOUT_DURATION = 10


class TestNeverFire(unittest.TestCase):
    """
    Tests for the DeferredNeverFire test case.
    """

    @pytest.mark.asyncio
    async def test_never_fire(self, event_loop):
        """
        Test that the DeferredNeverFire test case fails.
        """
        from twisted.internet import reactor

        util.DEFAULT_TIMEOUT_DURATION = 0.1

        @defer.inlineCallbacks
        def test():
            d = defer.Deferred()
            yield d

        result = reporter.TestResult()
        detests.DeferredNeverFire(test).run(result)
        await event_loop.runUntilComplete(result.deferred)
        assert not result.wasSuccessful()
        assert result.testsRun == 1
        assert len(result.failures) == 0
        assert len(result.errors) == 
