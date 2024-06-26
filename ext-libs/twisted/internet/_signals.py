# -*- test-case-name: twisted.internet.test.test_sigchld -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module is used to integrate child process termination into a
reactor event loop.  This is a challenging feature to provide because
most platforms indicate process termination via SIGCHLD and do not
provide a way to wait for that signal and arbitrary I/O events at the
same time.  The naive implementation involves installing a Python
SIGCHLD handler; unfortunately this leads to other syscalls being
interrupted (whenever SIGCHLD is received) and failing with EINTR
(which almost no one is prepared to handle).  This interruption can be
disabled via siginterrupt(2) (or one of the equivalent mechanisms);
however, if the SIGCHLD is delivered by the platform to a non-main
thread (not a common occurrence, but difficult to prove impossible),
the main thread (waiting on select() or another event notification
API) may not wake up leading to an arbitrary delay before the child
termination is noticed.

The basic solution to all these issues involves enabling SA_RESTART
(ie, disabling system call interruption) and registering a C signal
handler which writes a byte to a pipe.  The other end of the pipe is
registered with the event loop, allowing it to wake up shortly after
SIGCHLD is received.  See L{twisted.internet.posixbase._SIGCHLDWaker}
for the implementation of the event loop side of this solution.  The
use of a pipe this way is known as the U{self-pipe
trick<http://cr.yp.to/docs/selfpipe.html>}.

From Python version 2.6, C{signal.siginterrupt} and C{signal.set_wakeup_fd}
provide the necessary C signal handler which writes to the pipe to be
registered with C{SA_RESTART}.
"""

from __future__ import division, absolute_import

import signal

def install_handler(fd: int) -> int:
    """
    Install a signal handler which will write a byte to fd when
    SIGCHLD is received.

    This is implemented by installing a SIGCHLD handler that does nothing,
    setting the SIGCHLD handler as not allowed to interrupt system calls,
    and using signal.set_wakeup_fd to do the actual writing.

    @param fd: The file descriptor to which to write when SIGCHLD is
        received.
    @type fd: int
    """
    if fd == -1:
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    else:
        def noop_signal_handler(*args):
            pass
        signal.signal(signal.SIGCHLD, noop_signal_handler)
        signal.siginterrupt(signal.SIGCHLD, False)
    return signal.set_wakeup_fd(fd)

def is_default_handler() -> bool:
    """
    Determine whether the SIGCHLD handler is the default or not.
    """
    return signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL
