# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys
import unittest
from twisted.python.runtime import platform
from twisted.python.util import sibpath
from twisted.internet.utils import getProcessOutputAndValue
from twisted.plugins.twisted_qtstub import errorMessage
from twisted.internet.qtreactor import Qtreactor  # Added for the test


class QtreactorTestCase(unittest.TestCase):
    """
    Tests for L{twisted.internet.qtreactor}.
    """

    def test_importQtreactor(self):
        """
        Test that attempting to import L{twisted.internet.qtreactor} raises
        an ImportError indicating that C{qtreactor} is no longer a part of
        Twisted.
        """
        original_qtreactor = sys.modules.get('qtreactor')
        try:
            sys.modules['qtreactor'] = None
            with self.assertRaises(ImportError) as cm:
                import twisted.internet.qtreactor
            self.assertEqual(str(cm.exception), f"No module named 'qtreactor'; "
                                                f"twisted.internet.qtreactor "
                                                f"has been removed. See {errorMessage} "
                                                f"for details.")
        finally:
            sys.modules['qtreactor'] = original_qtreactor


skipWindowsNopywin32 = None
if platform.isWindows():
    try:
        import win32process
    except ImportError:
        skipWindowsNopywin32 = ("On windows, spawnProcess
