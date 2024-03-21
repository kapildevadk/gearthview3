# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for twisted.python.modules, abstract access to imported or importable
objects.
"""

import sys
import itertools
import zipfile
import compileall
from collections.abc import Iterable
from typing import List, Any

import twisted
from twisted.trial.unittest import TestCase
from twisted.python import modules, filepath
from twisted.python.reflect import namedAny


class TwistedModulesMixin:
    """
    Mixin for L{TwistedModulesTestCase} to provide helper methods.
    """

    def find_by_iteration(self, modname: str, where: modules.PythonPath = modules,
                          import_packages: bool = False) -> modules.ModuleInfo:
        """
        Iterate over modules and find the given module name.
        """
        for modinfo in where.walkModules(import_packages=import_packages):
            if modinfo.name == modname:
                return modinfo
        self.fail(f"Unable to find module {modname} through iteration.")


class TwistedModulesTestCase(TwistedModulesMixin, TestCase):
    """
    Base class for L{modules} test cases.
    """

    def test_namespaced_packages(self):
        """
        Duplicate packages are not yielded when iterating over namespace
        packages.
        """
        # Force pkgutil to be loaded already
        import pkgutil

        namespace_boilerplate = (
            'import pkgutil; '
            '__path__ = pkgutil.extend_path(__path__, __name__)')

        # Create two temporary directories with packages
        entry = filepath.FilePath(self.mktemp())
        test_package_path = entry.child('test_package')
        test_package_path.child('__init__.py').setContent(namespace_boilerplate)

        nested_entry = test_package_path.child('nested_package')
        nested_entry.makedirs()
        nested_entry.child('__init__.py').setContent(namespace_boilerplate)
        nested_entry.child('module.py').setContent('')

        another_entry = filepath.FilePath(self.mktemp())
        another_package_path = another_entry.child('test_package')
        another_package_path.child('__init__.py').setContent(namespace_boilerplate)

        another_nested_entry = another_package_path.child('nested_package')
        another_nested_entry.makedirs()
        another_nested_entry.child('__init__.py').setContent(namespace_boilerplate)
        another_nested_entry.child('module2.py').setContent('')

        sys.path[:] = [entry.path, another_entry.path]

        module = modules.getModule('test_package')

        try:
            walked_names = [
                mod.name for mod in module.walkModules(import_packages=True)]
        finally:
            for module in sys.modules.keys():
                if module.startswith('test_package'):
                    del sys.modules[module]

        expected = [
            'test_package',
            'test_package.nested_package',
            'test_package.nested_package.module',
            'test_package.nested_package.module2',
        ]

        self.assertEqual(walked_names, expected)


class BasicTests(TwistedModulesTestCase):

    def test_unimportable_package_getitem(self):
        """
        If a package has been explicitly forbidden from importing by setting a
        C{None} key in sys.modules under its name,
        L{modules.PythonPath.__getitem__} should still be able to retrieve an
        unloaded L{modules.PythonModule} for that package.
        """
        should_not_load = []
        path = modules.PythonPath(
            sys_path=[self.pathEntryWithOnePackage().path],
            module_loader=should_not_load.append,
            importer_cache={},
            sys_path_hooks={},
            module_dict={'test_package': None})
        self.assertEqual(should_not_load, [])
        self.assertEqual(path['test_package'].isLoaded(), False)


    def test_unimportable_package_walk_modules(self):
        """
        If a package has been explicitly forbidden from importing by setting a
        C{None} key in sys.modules under its name, L{modules.walkModules} should
        still be able to retrieve an unloaded L{modules.PythonModule} for that
        package.
        """
        existent_path = self.pathEntryWithOnePackage()
        self.replaceSysPath([existent_path.path])
        self.replaceSysModules({"test_package": None})

        walked = list(modules.walkModules())
        self.assertEqual([mod.name for mod in walked],
                          ["test_package"])
        self.assertEqual(walked[0].isLoaded(), False)


    def test_nonexistent_paths(self):
        """
        Verify that L{modules.walkModules} ignores entries in sys.path which
        do not exist in the filesystem.
        """
        existent_path = self.pathEntryWithOnePackage()

        nonexistent_path = filepath.FilePath(self.mktemp())
        self.failIf(nonexistent_path.exists())

        self.replaceSysPath([existent_path.path])

        expected = [modules.getModule("test_package")]

        before_modules = list(modules.walkModules())
        sys.path.append(nonexistent_path.path)
        after_modules = list(modules.walkModules())

        self.assertEqual(before_modules, expected)
        self.
