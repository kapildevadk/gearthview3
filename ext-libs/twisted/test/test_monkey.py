# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.monkey}.
"""

from __future__ import division, absolute_import

import unittest
from unittest.mock import patch, Mock, PropertyMock


class TestObj:
    def __init__(self):
        self.foo = 'foo value'
        self.bar = 'bar value'
        self.baz = 'baz value'


class MonkeyPatcherTest(unittest.TestCase):
    """
    Tests for L{MonkeyPatcher} monkey-patching class.
    """

    def setUp(self):
        self.test_object = TestObj()
        self.original_object = TestObj()

    @patch('__main__.TestObj.foo', new_callable=PropertyMock)
    @patch('__main__.TestObj.bar', new_callable=PropertyMock)
    def test_empty(self, mock_bar, mock_foo):
        """
        A monkey patcher without patches shouldn't change a thing.
        """
        mock_foo.return_value = self.test_object.foo
        mock_bar.return_value = self.test_object.bar

        # We can't assert that all state is unchanged, but at least we can
        # check our test object.
        self.assertEqual(self.original_object.foo, self.test_object.foo)
        self.assertEqual(self.original_object.bar, self.test_object.bar)
        self.assertEqual(self.original_object.baz, self.test_object.baz)

        mock_foo.assert_called_once_with('foo value')
        mock_bar.assert_called_once_with('bar value')

    @patch('__main__.TestObj.foo', new_callable=PropertyMock)
    @patch('__main__.TestObj.bar', new_callable=PropertyMock)
    def test_construct_with_patches(self, mock_bar, mock_foo):
        """
        Constructing a L{MonkeyPatcher} with patches should add all of the
        given patches to the patch list.
        """
        mock_foo.return_value = 'haha'
        mock_bar.return_value = 'hehe'

        patcher = MonkeyPatcher([(self.test_object, 'foo', 'haha'),
                                (self.test_object, 'bar', 'hehe')])
        patcher.patch()

        self.assertEqual('haha', self.test_object.foo)
        self.assertEqual('hehe', self.test_object.bar)
        self.assertEqual(self.original_object.baz, self.test_object.baz)

        mock_foo.assert_called_once_with('haha')
        mock_bar.assert_called_once_with('hehe')

    @patch('__main__.TestObj.foo', new_callable=PropertyMock)
    def test_patch_existing(self, mock_foo):
        """
        Patching an attribute that exists sets it to the value defined in the
        patch.
        """
        mock_foo.return_value = 'haha'

        self.test_object.foo = 'blah'

        self.monkey_patcher.add_patch(self.test_object, 'foo', 'haha')
        self.monkey_patcher.patch()

        self.assertEqual(self.test_object.foo, 'haha')

        mock_foo.assert_called_once_with('haha')

    @patch('__main__.TestObj.nowhere', new_callable=PropertyMock)
    def test_patch_non_existing(self, mock_nowhere):
        """
        Patching a non-existing attribute fails with an C{AttributeError}.
        """
        self.assertRaises(AttributeError, self.monkey_patcher.patch)

        mock_nowhere.assert_not_called()

    @patch('__main__.TestObj.foo', new_callable=PropertyMock)
    def test_patch_already_patched(self, mock_foo):
        """
        Adding a patch for an object and attribute that already have a patch
        overrides the existing patch.
        """
        mock_foo.return_value = 'blah'

        self.monkey_patcher.add_patch(self.test_object, 'foo', 'blah')
        self.monkey_patcher.add_patch(self.test_object, 'foo', 'BLAH')
        self.monkey_patcher.patch()

        self.assertEqual(self.test_object.foo, 'BLAH')

        mock_foo.assert_called_once_with('BLAH')

    @patch('__main__.TestObj.foo', new_callable=PropertyMock)
    def test_restore_twice_is_a_no_op(self, mock_foo):
        """
        Restoring an already-restored monkey
