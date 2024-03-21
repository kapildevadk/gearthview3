# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.release} and L{twisted.python._release}.

All of these tests are skipped on platforms other than Linux, as the release is
only ever performed on Linux.
"""

import glob
import warnings
import operator
import os
import sys
from StringIO import StringIO
import tarfile
from xml.dom import minidom as dom

from datetime import date

from twisted.trial.unittest import TestCase

from twisted.python.compat import execfile
from twisted.python.procutils import which
from twisted.python.filepath import FilePath
from twisted.python.versions import Version
from twisted.test.testutils import XMLAssertionMixin
from twisted.python._release import (
    _changeVersionInFile, getNextVersion, findTwistedProjects, replaceInFile,
    replaceProjectVersion, Project, generateVersionFileData,
    changeAllProjectVersions, VERSION_OFFSET, DocBuilder, ManBuilder,
    NoDocumentsFound, filePathDelta, CommandFailed, BookBuilder,
    DistributionBuilder, APIBuilder, BuildAPIDocsScript, buildAllTarballs,
    runCommand, UncleanWorkingDirectory, NotWorkingDirectory,
    ChangeVersionsScript, BuildTarballsScript, NewsBuilder
)

if os.name != 'posix':
    skip = "Release toolchain only supported on POSIX."
else:
    skip = None


# Check a bunch of dependencies to skip tests if necessary.
try:
    from twisted.lore.scripts import lore
except ImportError:
    loreSkip = "Lore is not present."
else:
    loreSkip = skip


try:
    import pydoctor.driver
    # it might not be installed, or it might use syntax not available in
    # this version of Python.
except (ImportError, SyntaxError):
    pydoctorSkip = "Pydoctor is not present."
else:
    if getattr(pydoctor, "version_info", (0,)) < (0, 1):
        pydoctorSkip = "Pydoctor is too old."
    else:
        pydoctorSkip = skip


if which("latex") and which("dvips") and which("ps2pdf13"):
    latexSkip = skip
else:
    latexSkip = "LaTeX is not available."


if which("svn") and which("svnadmin"):
    svnSkip = skip
else:
    svnSkip = "svn or svnadmin is not present."


def gen_version(*args, **kwargs):
    """
    A convenience for generating _version.py data.

    @param args: Arguments to pass to L{Version}.
    @param kwargs: Keyword arguments to pass to L{Version}.
    """
    return generateVersionFileData(Version(*args, **kwargs))


class StructureAssertingMixin(object):
    """
    A mixin for L{TestCase} subclasses which provides some methods for
    asserting the structure and contents of directories and files on the
    filesystem.
    """
    def create_structure(self, root, dir_dict):
        """
        Create a set of directories and files given a dict defining their
        structure.

        @param root: The directory in which to create the structure.  It must
            already exist.
        @type root: L{FilePath}

        @param dir_dict: The dict defining the structure. Keys should be strings
            naming files, values should be strings describing file contents OR
            dicts describing subdirectories.  All files are written in binary
            mode.  Any string values are assumed to describe text files and
            will have their newlines replaced with the platform-native newline
            convention.  For example::

                {"foofile": "foocontents",
                 "bardir": {"barfile": "bar\ncontents"}}
        @type dir_dict: C{dict}
        """
        for x in dir_dict:
            child = root.child(x)
            if isinstance(dir_dict[x], dict):
                child.createDirectory()
                self.create_structure(child, dir_dict[x])
            else:
                child.setContent(dir_dict[x].replace('\n', os.linesep))

    def assert_structure(self, root, dir_dict):
        """
        Assert that a directory is equivalent to one described by a dict.

        @param root: The filesystem directory to compare.
        @type root: L{FilePath}
        @param dir_dict: The dict that should describe the contents of the
            directory. It should be the same structure as the C{dir_dict}
            parameter to L{create_structure}.
        @type dir_dict: C{dict}
        """
        children = [x.basename() for x in root.children()]
        for x in dir_dict:
            child = root.child(x)
            if isinstance(dir_dict[x], dict):
                self.assertTrue(child.isdir(), "%s is not a dir!"
                                % (child.path,))
                self.assert_structure(child, dir_dict[x])
            else:
                a = child.getContent().replace(os.linesep, '\n')
                self.assertEqual(a, dir_dict[x], child.path)
            children.remove(x)
        if children:
            self.fail("There were extra children in %s: %s"
                      % (root.path, children))



class ChangeVersionTest(TestCase, StructureAssertingMixin):
    """
    Twisted has the ability to change versions.
    """

    def make_file(self, relative_path, content):
        """
        Create a file with the given content relative to a temporary directory.

        @param relative_path: The basename of the file to create.
        @param content: The content that the file will have.
        @return: The filename.
        """
        base_directory = FilePath(self.mktemp())
        directory
