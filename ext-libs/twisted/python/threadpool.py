# -*- test-case-name: twisted.test.test_threadpool -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
twisted.python.threadpool: a pool of threads to which we dispatch tasks.

In most cases you can just use C{reactor.callInThread} and friends
instead of creating a thread pool directly.
"""

from __future__ import division, absolute_import

import threading
import queue
import copy
from typing import Callable, Any, Union, List, Tuple
import contextvars
import logging

from twisted.python import log, context, failure

class ThreadPoolException(Exception):
    """Exception raised by the ThreadPool class."""

class WorkerStop:
    """Object used to signal a worker thread to stop."""

class ThreadPool:
    """
    This class (hopefully) generalizes the functionality of a pool of
    threads to which work can be dispatched.

    L{callInThread} and L{stop} should only be called from
    a single thread, unless you make a subclass where L{stop} and
    L{_startSomeWorkers} are synchronized.
    """
    min: int
    max: int
    joined: bool
    started: bool
    workers: int
    name: str

    thread_factory = threading.Thread
    current_thread = staticmethod(threading.current_thread)

    def __init__(self, minthreads: int = 5, maxthreads: int = 20, name: str = None):
        """
        Create a new threadpool.

        @param minthreads: minimum number of threads in the pool
        @param maxthreads: maximum number of threads in the pool
        """
        self.q = queue.Queue(0)
        self.min = minthreads
        self.max = maxthreads
        self.name = name
        self.waiters: List[threading.Thread] = []
        self.threads: List[threading.Thread] = []
        self.working: List[threading.Thread] = []

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return (
            f"<ThreadPool min={self.min}, max={self.max}, "
            f"joined={self.joined}, started={self.started}, "
            f"workers={self.workers}, name={self.name}>"
        )

    def start(self) -> None:
        """Start the threadpool."""
        self.joined = False
        self.started = True
        # Start some threads.
        self.adjustPoolsize()

    def startAWorker(self) -> None:
        self.workers += 1
        name = f"PoolThread-{self.name or id(self)}-{self.workers}"
        new_thread = self.thread_factory(target=self._worker, name=name)
        self.threads.append(new_thread)
        new_thread.start()

    def stopAWorker(self) -> None:
        self.q.put(WorkerStop)
        self.workers -= 1

    def __setstate__(self, state: dict) -> None:
        self.__dict__ = state
        ThreadPool.__init__(self, self.min, self.max)

    def __getstate__(self) -> dict:
        state = {}
        state['min'] = self.min
        state['max'] = self.max
        return state

    def _startSomeWorkers(self) -> None:
        needed_size = self.q.qsize() + len(self.working)
        # Create enough, but not too many
        while self.workers < min(self.max, needed_size):
            self.startAWorker()

    def callInThread(self, func: Callable[[], Any], *args: Tuple, **kw: dict) -> None:
        """
        Call a callable object in a separate thread.

        @param func: callable object to be called in separate thread

        @param *args: positional arguments to be passed to C{func}

        @param **kw: keyword args to be passed to C{func}
        """
        self.callInThreadWithCallback(None, func, *args, **kw)

    def callInThreadWithCallback(
        self, on_result: Callable[[bool, Union[Any, failure.Failure]], Any],
        func: Callable[[], Any], *args: Tuple, **kw: dict
    ) -> None:
        """
        Call a callable object in a separate thread and call C{onResult}
        with the return value, or a L{twisted.python.failure.Failure}
        if the callable raises an exception.

        The callable is allowed to block, but the C{onResult} function
        must not block and should perform as little work as possible.

        A typical action for C{onResult} for a threadpool used with a
        Twisted reactor would be to schedule a
        L{twisted.internet.defer.Deferred} to fire in the main
        reactor thread using C{.callFromThread}.  Note that C{onResult}
        is called inside the separate thread, not inside the reactor thread.

        @param onResult: a callable with the signature C{(success, result)}.
            If the callable returns normally, C{onResult} is called with
            C{(True, result)} where C{result} is the return value of the
            callable. If the callable throws an exception, C{onResult} is
            called with C{(False, failure)}.

            Optionally, C{onResult} may be C{None}, in which case it is not
            called
