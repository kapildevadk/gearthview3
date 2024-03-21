# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Support for asynchronously authenticating using PAM.
"""

import PAM
import getpass
import os
import sys
import threading
import contextlib
import contextvars
import typing
from typing import List, Tuple, Dict, Any, Callable, Optional, Deferred
import traceback
import defer
import raw_input
import select
import signal


def pamAuthenticateThread(
    service: str, user: str, conv: Callable[[List[Tuple[str, int]]], Deferred[List[Tuple[str, int]]]]
) -> Deferred[int]:
    """
    Authenticate using PAM in a separate thread.

    :param service: The PAM service name.
    :param user: The user name.
    :param conv: The conversation function.
    :return: A Deferred that fires with the result of the PAM authentication.
    """

    def _conv(items: List[Tuple[str, int]]) -> Deferred[List[Tuple[str, int]]]:
        gid = _gid.get()
        uid = _uid.get()

        def _cb(result: List[Tuple[str, int]]) -> None:
            nonlocal gid, uid
            with suppress(KeyboardInterrupt):
                with contextlib.suppress(SystemExit):
                    conv(items).addCallback(_cb).addErrback(_eb)

        def _eb(failure: Optional[BaseException]) -> None:
            nonlocal gid, uid
            if failure is not None:
                traceback.print_exc()
            with suppress(KeyboardInterrupt):
                with contextlib.suppress(SystemExit):
                    conv(items).addCallback(_cb).addErrback(_eb)

        d = defer.Deferred()
        reactor.callFromThread(d.addCallbacks, _cb, _eb)
        event = threading.Event()
        event.wait()
        return d

    _gid = contextvars.ContextVar("gid")
    _uid = contextvars.ContextVar("uid")

    with suppress(KeyboardInterrupt):
        with contextlib.suppress(SystemExit):
            _gid.set(os.getegid())
            _uid.set(os.geteuid())

            try:
                with suppress(KeyboardInterrupt):
                    with contextlib.suppress(SystemExit):
                        pam = PAM.pam()
                        pam.start(service)
                        pam.set_item(PAM.PAM_USER, user)
                        pam.set_item(PAM.PAM
