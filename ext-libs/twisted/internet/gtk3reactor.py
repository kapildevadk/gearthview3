# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module provides support for Twisted to interact with the gtk3 mainloop
via Gobject introspection. This is like gi, but slightly slower and requires a
working $DISPLAY.

In order to use this support, simply do the following::

    from twisted.internet import gtk3reactor
    gtk3reactor.install()

If you wish to use a GApplication, register it with the reactor::

    from twisted.internet import reactor
    reactor.registerGApplication(app)

Then use twisted.internet APIs as usual.
"""

from __future__ import division, absolute_import

import os

from twisted.internet import gireactor
from twisted.python import runtime
from twisted.internet.interfaces import IReactorCore
from twisted.internet.main import installReactor


def check_display():
    """Check if $DISPLAY is set and raise an ImportError if not."""
    if (runtime.platform.getType() == "posix" and
            not runtime.platform.isMacOSX() and not os.environ.get("DISPLAY")):
        raise ImportError(
            "Gtk3 requires X11, and no DISPLAY environment variable is set"
        )


class Gtk3Reactor(gireactor.GIReactor):
    """A reactor using the gtk3+ event loop."""

    def __init__(self, use_gtk: bool = True):
        """Initialize the reactor."""
        gireactor.GIReactor.__init__(self, useGtk=use_gtk)


class PortableGtk3Reactor(gireactor.PortableGIReactor):
    """Portable GTK+ 3.x reactor."""

    def __init__(self, use_gtk: bool = True):
        """Initialize the reactor."""
        gireactor.PortableGIReactor.__init__(self, useGtk=use_gtk)


def install() -> IReactorCore:
    """
    Configure the Twisted mainloop to be run inside the gtk3+ mainloop.

    Returns:
        IReactorCore: The newly installed reactor.
    """
    check_display()

    if runtime.platform.getType() == "posix":
        reactor = Gtk3Reactor()
    else:
        reactor = PortableGtk3Reactor()

    installReactor(reactor)
    return reactor


if __name__ == "__main__":
    install()
