# -*- test-case-name: twisted.internet.test.test_utilspy3 -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Utility methods, ported to Python 3.
"""

from __future__ import division, absolute_import

import sys
import warnings
from functools import wraps
from typing import Callable, List, Tuple, Any, Union, Optional
from twisted.python.compat import reraise
from twisted.internet import defer

def _resetWarningFilters(passthrough: Optional[Callable], added_filters: List[Tuple[str, int, str]]) -> Optional[Callable]:
    for f in added_filters:
        if len(warnings.filters) >= len(added_filters):
            warnings.filters.remove(f)
    return passthrough

def runWithWarningsSuppressed(suppressed_warnings: List[Tuple[str, dict]], f: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Run the function `f`, but with some warnings suppressed.

    Args:
        suppressed_warnings: A list of arguments to pass to filterwarnings.
                               Must be a sequence of 2-tuples (args, kwargs).
        f: A callable, followed by its arguments and keyword arguments

    Returns:
        The result of calling `f` with the given arguments and keyword arguments.
    """
    with warnings.catch_warnings():
        for args_, kwargs_ in suppressed_warnings:
            warnings.filterwarnings(*args_, **kwargs_)
        added_filters = warnings.filters[:len(suppressed_warnings)]
        try:
            result = f(*args, **kwargs)
        except Exception as e:  # pylint: disable=broad-except
            exc_info = sys.exc_info()
            _resetWarningFilters(None, added_filters)
            reraise(exc_info[1], exc_info[2], from_=e)
        else:
            if isinstance(result, defer.Deferred):
                result.addBoth(_resetWarningFilters, added_filters)
            else:
                _resetWarningFilters(None, added_filters)
            return result

def suppressWarnings(f: Callable[..., Any], *suppressed_warnings: Tuple[str, dict]) -> Callable[..., Any]:
    """
    Wrap `f` in a callable which suppresses the indicated warnings before
    invoking `f` and unsuppresses them afterwards.  If f returns a Deferred,
    warnings will remain suppressed until the
