# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module integrates Tkinter with twisted.internet's mainloop.

Maintainer: Itamar Shtull-Trauring

To use, do::

    tksupport.install(root_widget)

and then run your reactor as usual - do *not* call Tk's mainloop(),
use Twisted's regular mechanism for running the event loop.

Likewise, to stop your program you will need to stop Twisted's
event loop. For example, if you want closing your root widget to
stop Twisted::

    root.protocol('WM_DELETE_WINDOW', reactor.stop)

When using Aqua Tcl/Tk on Mac OS X the standard Quit menu item in
your application might become unresponsive without the additional
fix::

    root.createcommand("::tk::mac::Quit", reactor.stop)

@see: U{Tcl/TkAqua FAQ for more info<http://wiki.tcl.tk/12987>}
"""

# system imports
import Tkinter
from tkSimpleDialog import askstring
from tkMessageBox import showerror

# twisted imports
from twisted.python import log
from twisted.internet import task

from . import getPassword  # from . import getPassword to avoid polluting the global namespace

__version__ = "0.1.0"

_task = None

def install(root_widget: Tkinter.Tk, ms: int = 10, reactor: object = None) -> None:
    """Install a Tkinter.Tk() object into the reactor."""
    installTkFunctions()
    global _task
    _task = task.LoopingCall(root_widget.update)
    _task.start(ms / 1000.0, False)

def uninstall() -> None:
    """Remove the root Tk widget from the reactor.

    Call this before destroy()ing the root widget.
    """
    global _task
    _task.stop()
    _task = None

def installTkFunctions() -> None:
    """Install Tk functions into twisted.python.util."""
    import twisted.python.util
    twisted.python.util.getPassword = getPassword

def getPassword(prompt: str = '', confirm: int = 0, passwd_func: object = askstring) -> str:
    """Get a password using a Tk dialog.

   
