# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for the flattening portion of L{twisted.web.template}, implemented in
L{twisted.web._flatten}.
"""

import sys
import traceback
from xml.etree.cElementTree import XML
from zope.interface import implements, implementer
from twisted.trial.unittest import TestCase
from twisted.test.testutils import XMLAssertionMixin
from twisted.internet.defer import DeferredList, succeed, fail
from twisted.web.iweb import IRenderable
from twisted.web.error import UnfilledSlot, UnsupportedType, FlattenerError
from twisted.web.template import tags, Tag, Comment, CDATA, CharRef, slot
from twisted.web.template import Element, renderer, TagLoader, flattenString
from twisted.web.test._util import FlattenTestCase
from typing import List, Tuple, Dict, Any, Union, Callable
from collections import OrderedDict


class OrderedAttributes(object):
    """
    An L{OrderedAttributes} is a stand-in for the L{Tag.attributes} dictionary
    that orders things in a deterministic order.  It doesn't do any sorting, so
    whatever order the attributes are passed in, they will be returned.

    @ivar attributes: The result of a L{dict}C{.items} call.
    @type attributes: L{list} of 2-L{tuples}
    """

    def __init__(self, attributes: Dict[str, Any]):
        self.attributes = list(attributes.items())


    def iteritems(self):
        """
        Like L{dict}C{.iteritems}.

        @return: an iterator
        @rtype: list iterator
        """
        return iter(self.attributes)


class TestSerialization(FlattenTestCase, XMLAssertionMixin):
    """
    Tests for flattening various things.
    """

    def test_nestedTags(self):
        """
        Test that nested tags flatten correctly.
        """
        return self.assertFlattensTo(
            tags.html(tags.body('42'), hi='there'),
            '<html hi="there"><body>42</body></html>')


    def test_serializeString(self):
        """
        Test that strings will be flattened and escaped correctly.
        """
        return DeferredList([
            self.assertFlattensTo('one', 'one'),
            self.assertFlattensTo('<abc&&>123', '&lt;abc&amp;&amp;&gt;123'),
        ])


    def test_serializeSelfClosingTags(self):
        """
        The serialized form of a self-closing tag is C{'<tagName />'}.
        """
        return self.assertFlattensTo(tags.img(), '<img />')


    def test_serializeAttribute(self):
        """
        The serialized form of attribute I{a} with value I{b} is C{'a="b"'}.
        """
        self.assertFlattensImmediately(tags.img(src='foo'),
                                       '<img src="foo" />')


    def test_serializedMultipleAttributes(self):
        """
        Multiple attributes are separated by a single space in their serialized
        form.
        """
        tag = tags.img()
        tag.attributes = OrderedAttributes([("src", "foo"), ("name", "bar")])
        self.assertFlattensImmediately(tag, '<img src="foo" name="bar" />')


    def checkAttributeSanitization(self, wrapData: Callable[[bytes], Any],
                                   wrapTag: Callable[[Tag], Any]):
        """
        Common implementation of L{test_serializedAttributeWithSanitization}
        and L{test_serializedDeferredAttributeWithSanitization},
        L{test_serializedAttributeWithTransparentTag}.

        @param wrapData: A 1-argument callable that wraps around the
            attribute's value so other tests can customize it.
        @param wrapData: callable taking L{bytes} and returning something
            flattenable

        @param wrapTag: A 1-argument callable that wraps around the outer tag
            so other tests can customize it.
        @type wrapTag: callable taking L{Tag} and returning L{Tag}.
        """
        self.assertFlattensImmediately(
            wrapTag(tags.img(src=wrapData("<>&\""))),
            '<img src="&lt;&gt;&amp;&quot;" />')


    def test_serializedAttributeWithSanitization(self):
        """
        Attribute values containing C{"<"}, C{">"}, C{"&"}, or C{'"'} have
        C{"&lt;"}, C{"&gt;"}, C{"&amp;"}, or C
