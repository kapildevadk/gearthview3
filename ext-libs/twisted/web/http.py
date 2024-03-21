# -*- test-case-name: twisted.web.test.test_http -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
HyperText Transfer Protocol implementation.

This is the basic server-side protocol implementation used by the Twisted
Web server.  It can parse HTTP 1.0 requests and supports many HTTP 1.1
features as well.  Additionally, some functionality implemented here is
also useful for HTTP clients (such as the chunked encoding parser).

"""

from __future__ import absolute_import, division

import os
import socket
import tempfile
import base64
import binascii
import calendar
import cgi
import math
import time
from io import BytesIO as StringIO
from urllib.parse import ParseResult, urlparse, unquote, parse_qs, parse_header
try:
    from urllib.parse import urlparse as _urlparse
except ImportError:
    from urlparse import urlparse as _urlparse

try:
    from urlparse import ParseResultBytes, urlparse as _urlparse
    from urllib import unquote
    from cgi import parse_header as _parseHeader
except ImportError:
    from urllib.parse import ParseResultBytes, urlparse as _urlparse
    from io import TextIOWrapper

    def unquote(string, *args, **kwargs):
        return _unquote(string.decode('charmap'), *args, **kwargs).encode('charmap')

    def _parseHeader(line):
        key, pdict = cgi.parse_header(line.decode('charmap'))
        return (key.encode('charmap'), pdict)

from twisted.python.compat import _PY3
from twisted.internet import interfaces, reactor, protocol, address
from twisted.internet.defer import Deferred
from twisted.protocols import policies, basic
from twisted.python import log
from twisted.web.http_headers import _DictHeaders, Headers
from twisted.web._responses import (
    SWITCHING,
    OK, CREATED, ACCEPTED, NON_AUTHORITATIVE_INFORMATION, NO_CONTENT,
    RESET_CONTENT, PARTIAL_CONTENT, MULTI_STATUS,

    MULTIPLE_CHOICE, MOVED_PERMANENTLY, FOUND, SEE_OTHER, NOT_MODIFIED,
    USE_PROXY, TEMPORARY_REDIRECT,

    BAD_REQUEST, UNAUTHORIZED, PAYMENT_REQUIRED, FORBIDDEN, NOT_FOUND,
    NOT_ALLOWED, NOT_ACCEPTABLE, PROXY_AUTH_REQUIRED, REQUEST_TIMEOUT,
    CONFLICT, GONE, LENGTH_REQUIRED, PRECONDITION_FAILED,
    REQUEST_ENTITY_TOO_LARGE, REQUEST_URI_TOO_LONG,
    UNSUPPORTED_MEDIA_TYPE, REQUESTED_RANGE_NOT_SATISFIABLE,
    EXPECTATION_FAILED,

    INTERNAL_SERVER_ERROR, NOT_IMPLEMENTED, BAD_GATEWAY,
    SERVICE_UNAVAILABLE, GATEWAY_TIMEOUT, HTTP_VERSION_NOT_SUPPORTED,
    INSUFFICIENT_STORAGE_SPACE, NOT_EXTENDED,

    RESPONSES,
)

if _PY3:
    _intTypes = int
else:
    _intTypes = (int, long)

protocol_version = "HTTP/1.1"

CACHED = """Magic constant returned by http.Request methods to set cache
validation headers when the request is conditional and the value fails
the condition."""

# backwards compatability
responses = RESPONSES


# datetime parsing and formatting
weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
weekdayname_lower = [name.lower() for name in weekdayname]
monthname_lower = [name and name.lower() for name in monthname]

def urlparse(url):
    """
    Parse an URL into six components.

    This is similar to C{urlparse.urlparse}, but rejects C{unicode} input
    and always produces C{bytes} output.

    @type url: C{bytes}

    @raise TypeError: The given url was a C{unicode} string instead of a
        C{bytes}.

    @return: The scheme, net location, path, params, query string, and fragment
        of the URL - all as C{bytes}.
    @rtype: C{ParseResultBytes}
    """
    if isinstance(url, unicode):
        raise TypeError("url must be bytes, not unicode")
    scheme, netloc, path, params, query, fragment =
