# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from io import StringIO
import os
import re
from typing import Any, Dict, List, Optional, TextIO, TypeVar

import domhelpers
from latex import BaseLatexSpitter, entities
from tree import getHeaders, tree

