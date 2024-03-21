# -*- test-case-name: twisted.internet.test -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module provides support for Twisted to interact with the glib/gtk2
mainloop.
"""

import sys
from typing import Optional

import gobject
from twisted.internet import _glibbase, reactor, runtime
from twisted.python import runtime

try:
    if not hasattr(sys, 'frozen'):
        import pygtk
        pygtk.require('2.0')
except (ImportError, AttributeError):
    pass

if hasattr(gobject, "threads_init"):
    gobject.threads_init()

class Gtk2Reactor(_glibbase.GlibReactorBase):
    """
    PyGTK+ 2 event loop reactor.
    """
    _POLL_DISCONNECTED = gobject.IO_HUP | gobject.IO_ERR | gobject.IO_NVAL
    _POLL_IN = gobject.IO_IN
    _POLL_OUT = gobject.IO_OUT

    INFLAGS = _POLL_IN | _POLL_DISCONNECTED
    OUTFLAGS = _POLL_OUT | _POLL_DISCONNECTED

    def __init__(self, useGtk: Optional[bool] = True):
        _gtk = None
        if useGtk is True:
            import gtk as _gtk

        _glibbase.GlibReactorBase.__init__(self, gobject, _gtk, useGtk=useGtk)

def install(useGtk: Optional[bool] = True) -> reactor.IReactorCore:
    """
    Configure the twisted mainloop to be run inside the gtk mainloop.

    @param useGtk: should glib rather than GTK+ event loop be
        used (this will be slightly faster but does not support GUI).
    """
    reactor = Gtk2Reactor(useGtk)
    from twisted.internet.main import installReactor
    installReactor(reactor)
    return reactor

if runtime.platform.getType() != 'posix':
    install.__doc__ += '\nNote: This function is used on non-Posix platforms.'

__all__ = ['install']
