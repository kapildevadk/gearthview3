# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
HTTP errors.
"""

import unittest
from twisted.web.error import Error, PageRedirect, InfiniteRedirection

class HTTPErrorTests(unittest.TestCase):
    """
    Tests for how L{Error}, L{PageRedirect}, and L{InfiniteRedirection} attributes are initialized.
    """

    def test_error_no_message_valid_status(self):
        """
        If no C{message} argument is passed to the L{Error} constructor and the
        C{code} argument is a valid HTTP status code, C{code} is mapped to a
        descriptive string to which C{message} is assigned.
        """
        e = Error(status="200")
        self.assertEqual(e.message, "OK")


    def test_error_no_message_invalid_status(self):
        """
        If no C{message} argument is passed to the L{Error} constructor and
        C{code} isn't a valid HTTP status code, C{message} stays C{None}.
        """
        e = Error(status="InvalidCode")
        self.assertEqual(e.message, None)


    def test_error_message_exists(self):
        """
        If a C{message} argument is passed to the L{Error} constructor, the
        C{message} isn't affected by the value of C{status}.
        """
        e = Error(status="200", message="My own message")
        self.assertEqual(e.message, "My own message")


    def test_page_redirect_no_message_valid_status(self):
        """
        If no C{message} argument is passed to the L{PageRedirect} constructor
        and the C{code} argument is a valid HTTP status code, C{code} is mapped
        to a descriptive string to which C{message} is assigned.
        """
        e = PageRedirect(status="200", location="/foo")
        self.assertEqual(e.message, "OK to /foo")


    def test_page_redirect_no_message_valid_status_no_location(self):
        """
        If no C{message} argument is passed to the L{PageRedirect} constructor
        and C{location} is also empty and the C{code} argument is a valid HTTP
        status code, C{code} is mapped to a descriptive string to which
        C{message} is assigned without trying to include an empty location.
        """
        e = PageRedirect(status="200")
        self.assertEqual(e.message, "OK")


    def test_page_redirect_no_message_invalid_status(self):
        """
        If no C{message} argument is passed to the L{PageRedirect} constructor
        and C{code} isn't a valid HTTP status code, C{message} stays C{None}.
        """
        e = PageRedirect(status="InvalidCode", location="/foo")
        self.assertEqual(e.message, None)


    def test_page_redirect_message_exists_location_exists(self):
        """
        If a C{message} argument is passed to the L{PageRedirect} constructor,
        the C{message} isn't affected by the value of C{status}.
        """
        e = PageRedirect(status="200", message="My own message", location="/foo")
        self.assertEqual(e.message, "My own message to /foo")


    def test_page_redirect_message_exists_no_location(self):
        """
        If a C{message} argument is passed to the L{PageRedirect} constructor
        and no location is provided, C{message} doesn't try to include the empty
        location.
        """
        e = PageRedirect(status="200", message="My own message")
        self.assertEqual(e.message, "My own message")


    def test_infinite_redirection_no_message_valid_status(self):
        """
        If no C{message} argument is passed to the L{InfiniteRedirection}
        constructor and the C{code} argument is a valid HTTP status code,
        C{code} is mapped to a descriptive string to which C{message} is
        assigned.
        """
        e = InfiniteRedirection(status="200", location="/foo")
        self.assertEqual(e.message, "OK to /foo")


    def test_infinite_redirection_no_message_valid_status_no_location(self):
        """
        If no C{message} argument is passed to the L{InfiniteRedirection}
        constructor and C{location} is also empty and the C{code} argument is a
        valid HTTP status code, C{code} is mapped to a descriptive string to
        which C{message} is assigned without trying to include an empty
        location.
        """
        e = InfiniteRedirection(status="200")
        self.assertEqual(e.message, "OK")


    def test_infinite_redirection_no_message_invalid_status(self):
        """
        If no C{message} argument is passed to the L{InfiniteRedirection}
        constructor and C{code} isn't a valid HTTP status code, C{message} stays
        C{None}.
        """
        e = InfiniteRedirection(status="InvalidCode", location="/foo")
        self.assertEqual(e.message, None)


    def test_infinite_redirection_message_exists_location_exists(self):
        """
        If a C{message} argument is passed to the L{InfiniteRedirection}
        constructor, the C{message} isn't affected by the value of C{status}.
        """
        e = InfiniteRedirection(status="200", message="My own message", location="/
