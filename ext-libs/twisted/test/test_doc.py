# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import inspect
import glob
import pathlib
import atexit
from types import ModuleType
from unittest import TestCase, skip
from twisted.trial import unittest
from twisted.python import reflect
from twisted.python.modules import getModule
import importlib


def error_in_file(f: str, line: int = 17, name: str = '') -> str:
    """
    Return a filename formatted so emacs will recognize it as an error point

    @param line: Line number in file.  Defaults to 17 because that's about how
        long the copyright headers are.
    """
    return f"{f}:{line}:{name}"


class DocCoverage(TestCase):
    """
    Looking for docstrings in all modules and packages.
    """

    def setUp(self) -> None:
        self.package_names: list[str] = []
        for mod in getModule('twisted').walkModules():
            if mod.isPackage():
                self.package_names.append(mod.name)

    def test_modules(self) -> None:
        """
        Looking for docstrings in all modules.
        """
        docless: list[str] = []
        for package_name in self.package_names:
            if package_name in ('twisted.test',):
                continue
            try:
                package: ModuleType = reflect.namedModule(package_name)
            except ImportError as e:
                # This is testing doc coverage, not importability.
                pass
            else:
                docless.extend(self.modules_in_package(package_name, package))
        self.failIf(docless, f"No docstrings in module files:\n{('\n'.join(map(error_in_file, docless)),))}")

    def modules_in_package(self, package_name: str, package: ModuleType) -> list[str]:
        docless: list[str] = []
        directory: pathlib.Path = pathlib.Path(package.__file__).parent
        for modfile in glob.glob(directory / f"*.py"):
            module_name: str = inspect.getmodulename(str(modfile))
            if module_name == '__init__':
                continue
            if module_name in ('spelunk_gnome', 'gtkmanhole'):
                continue
            try:
                module: ModuleType = importlib.import_module(f"{package_name}.{module_name}")
            except Exception as e:
                pass
            else:
                if not inspect.getdoc(module):
                    docless.append(str(modfile))
        return docless

    def test_packages(self) -> None:
        """
        Looking for docstrings in all packages.
        """
        docless: list[str] = []
        for package_name in self.package_names:
            try:
                package: ModuleType = reflect.namedModule(package_name)
            except Exception as e:
                pass
            else:
                if not inspect.getdoc(package):
                    docless.append(package.__file__.replace('.pyc', '.py'))
        self.failIf(docless, f"No docstrings for package files\n{('\n'.join(map(error_in_file, docless)),))}")

    testModules.skip = "Activate me when you feel like writing docstrings, and fixing GTK crashing bugs."

def print_docless_on_exit() -> None:
    docless = []
    for test_case in unittest.TestLoader().loadTestsFromTestCase(DocCoverage):
        result = unittest.TextTestRunner(verbosity=0).run(test_case)
        docless.extend(modfile for _, modfile in result.errors)
    if docless:
        print(f"The following files have no docstrings:\n{('\n'.join(map(error_in_file, docless)),))}")

if __name__ == "__main__":
    atexit.register(print_docless_on_exit)
    unittest.main()


[tool.poetry]
name = "doc-coverage"
version = "0.1.0"
description = "A package for checking docstrings in Twisted modules and packages."
authors = ["Twisted Matrix Laboratories"]

[tool.poetry.dependencies]
python = "^3.8"
twisted = "^22.2.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
