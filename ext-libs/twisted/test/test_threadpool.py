# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.threadpool}.
"""

from __future__ import division, absolute_import

import pickle
import time
import weakref
import gc
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import threadpool
from threadpool import threadable
from twisted.trial import unittest
from twisted.python import context
from twisted.internet.defer import Deferred
from twisted.python.compat import _PY3


class Synchronization:
    """
    A class to test synchronization of calls made with various mechanisms.
    """

    def __init__(self, N: int, waiting: threading.Lock):
        self.N = N
        self.waiting = waiting
        self.lock = threading.Lock()
        self.runs = []
        self.failures = 0

    def run(self) -> None:
        """
        The testy part: this is supposed to be invoked serially from
        multiple threads.
        """
        if self.lock.acquire(False):
            if not len(self.runs) % 5:
                time.sleep(0.0002)
            self.lock.release()
        else:
            self.failures += 1

        self.lock.acquire()
        self.runs.append(None)
        if len(self.runs) == self.N:
            self.waiting.release()
        self.lock.release()

    synchronized = ["run"]


class ThreadPoolTestCase(unittest.SynchronousTestCase):
    """
    Test threadpools.
    """

    def getTimeout(self) -> float:
        """
        Return number of seconds to wait before giving up.
        """
        return 5

    def _waitForLock(self, lock: threading.Lock) -> None:
        for _ in range(1000000):
            if lock.acquire(False):
                break
            time.sleep(1e-5)
        else:
            self.fail("A long time passed without succeeding")

    def test_attributes(self) -> None:
        """
        L{ThreadPool.min} and L{ThreadPool.max} are set to the values passed to
        L{ThreadPool.__init__}.
        """
        pool = threadpool.ThreadPool(12, 22)
        self.assertEqual(pool.min, 12)
        self.assertEqual(pool.max, 22)

    def test_start(self) -> None:
        """
        L{ThreadPool.start} creates the minimum number of threads specified.
        """
        pool = threadpool.ThreadPool(0, 5)
        pool.start()
        self.addCleanup(pool.stop)
        self.assertEqual(len(pool.threads), 0)

        pool = threadpool.ThreadPool(3, 10)
        self.assertEqual(len(pool.threads), 0)
        pool.start()
        self.addCleanup(pool.stop)
        self.assertEqual(len(pool.threads), 3)

    def test_threadCreationArguments(self) -> None:
        """
        Test that creating threads in the threadpool with application-level
        objects as arguments doesn't result in those objects never being
        freed.
        """
        tp = threadpool.ThreadPool(0, 1)
        tp.start()
        self.addCleanup(tp.stop)

        def worker(arg: Any) -> None:
            pass

        class Dumb:
            pass

        unique = Dumb()

        worker_ref = weakref.ref(worker)
        unique_ref = weakref.ref(unique)

        tp.callInThread(worker, unique)

        del worker
        del unique
        gc.collect()

        self.assertEqual(unique_ref(), None)
        self.assertEqual(worker_ref(), None)


class RaceConditionTestCase(unittest.SynchronousTestCase):

    def getTimeout(self) -> float:
        """
        Return number of seconds to wait before giving up.
        """
        return 5

    def setUp(self) -> None:
        self.event = threading.Event()
        self.threadpool = threadpool.ThreadPool(0, 10)
        self.threadpool.start()

    def tearDown(self) -> None:
        del self.event
        self.threadpool.stop()
        del self.threadpool

    def test_synchronization(self) -> None:
        """
        Test a race condition: ensure that actions run in the pool synchronize
        with actions run in the main thread.
        """
        timeout = self.getTimeout()
        self.threadpool.callInThread(self.event.set)
        self.event.wait(timeout)
        self.event.clear()
        for _ in range(3):
            self.threadpool.callInThread(self.event.wait)
        self.threadpool.callInThread(self.event.set)
        self.event.wait(timeout)
        if not self.event.is_set():
            self.event.set()
            self.fail("Actions not synchronized")

    def test_singleThread(self) -> None:
        """
        The submission of a new job to a thread pool in response to the
        C{onResult} callback does not cause a new thread to be added to the
        thread pool.
        """
        # Ensure no threads running
        self.assertEqual(self.threadpool.workers, 0)

        event = threading.Event()
        event.clear()

        def onResult(success:
