# Copyright (c) 2009 Twisted Matrix Laboratories.
"""
Tests for GTK2 GUI manhole.
"""

import sys
import pygtk
import gtk
from twisted.trial.unittest import TestCase
from twisted.python.reflect import prefixedMethodNames
from twisted.manhole.ui.gtk2manhole import ConsoleInput


class GTK2RequirementError(Exception):
    pass


def check_gtk2_requirement():
    try:
        pygtk.require("2.0")
    except:
        raise GTK2RequirementError("GTK 2.0 not available")
    try:
        _ = gtk.gdk
    except ImportError:
        raise GTK2RequirementError("GTK 2.0 not available")
    except RuntimeError:
        raise GTK2RequirementError(
            "Old version of GTK 2.0 requires DISPLAY, and we don't have one."
        )
    if gtk.gtk_version[0] == 1:
        raise GTK2RequirementError(
            "Requested GTK 2.0, but 1.0 was already imported."
        )


class ConsoleInputTests(TestCase):
    """
    Tests for L{ConsoleInput}.
    """

    def setUp(self):
        check_gtk2_requirement()
        self.ci = ConsoleInput(None)

    def test_reverse_keymap(self):
        """
        Verify that a L{ConsoleInput} has a reverse mapping of the keysym names
        it needs for event handling to their corresponding keysym.
        """
        for event_name in prefixedMethodNames(ConsoleInput, "key_"):
            keysym_name = event_name.split("_")[-1]
            keysym_value = getattr(gtk.keysyms, keysym_name)
            self.assertEqual(self.ci.rkeymap[keysym_value], keysym_name)


if __name__ == "__main__":
    if len(sys.
