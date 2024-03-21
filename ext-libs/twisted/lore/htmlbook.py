# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.python.compat import execfile

class Book:
    """
    A class to represent a book with chapters and an index file.
    """

    def __init__(self, filename=None):
        """
        Initialize a new Book object.

        :param filename: The filename of the book configuration file.
        """
        self.chapters = []
        self.index_filename = None

        if filename:
            execfile(filename, globals())

    @property
    def get_files(self):
        """
        A read-only property to get the list of chapter filenames.

        :return: A list of chapter filenames.
        """
        return [c[0] for c in self.chapters]

    def get_number(self, filename):
        """
        Get the number associated with a chapter filename.

        :param filename: The filename of the chapter.
        :return: The number associated with the chapter or None if not found.
        """
        for chapter in self.chapters:
            if chapter[0] == filename:
                return chapter[1]
        return None

    def get_index_filename(self):
        """
        A read-only property to get the index filename.

        :return: The index filename or None if not set.
        """
        return self.index_filename

   
