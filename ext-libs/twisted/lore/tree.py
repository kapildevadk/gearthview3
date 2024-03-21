import argparse
import cgi
import cStringIO
import logging
import pathlib
import re
import sys
import textwrap
from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, TextIO, Union
import xml.etree.ElementTree as ET
from xml.sax import make_parser
from xml.sax.handler import ErrorHandler
from xml.sax.xmlreader import InputSource

class ParseError(Exception):
    def __init__(self, message: str, filename: str, line: int, column: int):
        super().__init__(message)
        self.filename = filename
        self.line = line
        self.column = column

