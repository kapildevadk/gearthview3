# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.lore.lint}.
"""

import sys
from xml.dom import minidom
from typing import TextIO, Union, Optional
from unittest.mock import patch

from twisted.trial.unittest import TestCase
from twisted.lore.lint import getDefaultChecker
from twisted.lore.process import ProcessingFailure


class DefaultTagCheckerTests(TestCase):
    """
    Tests for L{twisted.lore.lint.DefaultTagChecker}.
    """

    def test_quote(self,) -> None:
        """
        If a non-comment node contains a quote ('"'), the checker returned
        by L{getDefaultChecker} reports an error and raises
        L{ProcessingFailure}.
        """
        document_source = (
            '<html>'
            '<head><title>foo</title></head>'
            '<body><h1>foo</h1><div>"</div></body>'
            '</html>')
        document = minidom.parseString(document_source)
        filename = self.mktemp()
        checker = getDefaultChecker()

        output = StringIO()
        patch_sys = patch('sys.stdout', output)
        with patch_sys:
            with self.assertRaises(ProcessingFailure):
                checker.check(document, filename)

        patch_sys.restore()

        self.assertIn("contains quote", output.getvalue())


    def test_quoteComment(self,) -> None:
        """
        If a comment node contains a quote ('"'), the checker returned by
        L{getDefaultChecker} does not report an error.
        """
        document_source = (
            '<html>'
            '<head><title>foo</title></head>'
            '<body><h1>foo</h1><!-- " --></body>'
            '</html>')
        document = minidom.parseString(document_source)
        filename = self.mktemp()
        checker = getDefaultChecker()

        output = StringIO()
        patch_sys = patch('sys.stdout', output)
        with patch_sys:
            checker.check(document, filename)

        patch_sys.restore()

        self.assertEqual(output.getvalue(), "")


    def test_aNode(self,) -> None:
        """
        If there is an <a> tag in the document, the checker returned by
        L{getDefaultChecker} does not report an error.
        """
        document_source = (
            '<html>'
            '<head><title>foo</title></head>'
            '<body><h1>foo</h1><a>A link.</a></body>'
            '</html>')

        self.assertEqual(self._lintCheck(True, document_source), "")


    def test_textMatchesRef(self,) -> None:
        """
        If an I{a} node has a link with a scheme as its contained text, a
        warning is emitted if that link does not match the value of the
        I{href} attribute.
        """
        document_source = (
            '<html>'
            '<head><title>foo</title></head>'
            '<body><h1>foo</h1>'
            '<a href="http://bar/baz">%s</a>'
            '</body>'
            '</html>')
        self._lintCheck(True, document_source % ("http://bar/baz",))
        self.assertIn(
            "link text does not match href",
            self._lintCheck(False, document_source % ("http://bar/quux",)))


    def _lintCheck(self, expect_success: bool, source: str,) -> str:
        """
        Lint the given document source and return the output.

        @param expect_success: A flag indicating whether linting is expected
            to succeed or not.

        @param source: The document source to lint.

        @return: A C{str} of the output of linting.
        """
        document = minidom.parseString(source)
        filename = self.mktemp()
        checker = getDefaultChecker()

        if not filename:
            self.skipTest("Could not create temporary file")

        output = StringIO()
        patch_sys = patch('sys.stdout', output)
        with patch_sys:
            try:
                if expect_success:
                    checker.check(document, filename)
                else:
                    with self.assertRaises(ProcessingFailure):
                        checker.check(document, filename)
            finally:
                patch_sys.restore()

        return output.getvalue()
