# -*- test-case-name: twisted.conch.test.test_text -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Character attribute manipulation API

This module provides a domain-specific language (using Python syntax)
for the creation of text with additional display attributes associated
with it.  It is intended as an alternative to manually building up
strings containing ECMA 48 character attribute control codes.  It
currently supports foreground and background colors (black, red,
green, yellow, blue, magenta, cyan, and white), intensity selection,
underlining, blinking and reverse video.  Character set selection
support is planned.

Character attributes are specified by using two Python operations:
attribute lookup and indexing.  For example, the string \"Hello
world\" with red foreground and all other attributes set to their
defaults, assuming the name twisted.conch.insults.text.attributes has
been imported and bound to the name \"A\" (with the statement
C{from twisted.conch.insults.text import attributes as A}, for example) one
uses this expression::

 | A.fg.red[\"Hello world\"]

Other foreground colors are set by substituting their name for
\"red\".  To set both a foreground and a background color, this
expression is used::

 | A.fg.red[A.bg.green[\"Hello world\"]]

Note that either A.bg.green can be nested within A.fg.red or vice
versa.  Also note that multiple items can be nested within a single
index operation by separating them with commas::

 | A.bg.green[A.fg.red[\"Hello\"], " ", A.fg.blue[\"world\"]]

Other character attributes are set in a similar fashion.  To specify a
blinking version of the previous expression::

 | A.blink[A.bg.green[A.fg.red[\"Hello\"], " ", A.fg.blue[\"world\"]]]

C{A.reverseVideo}, C{A.underline}, and C{A.bold} are also valid.

A third operation is actually supported: unary negation.  This turns
off an attribute when an enclosing expression would otherwise have
caused it to be on.  For example::

 | A.underline[A.fg.red[\"Hello\", -A.underline[\" world\"]]]

@author: Jp Calderone
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import twisted.conch.insults.helper as helper
import twisted.conch.insults.insults as insults


class _Attribute:
    def __init__(self):
        self.children = []

    def __getitem__(self, item: Union[str, "Attribute"]) -> "_Attribute":
        if isinstance(item, str):
            self.children.append(item)
        elif isinstance(item, Attribute):
            self.children.extend(item.children)
        else:
            raise TypeError("item must be a string or Attribute")
        return self

    def __call__(self, attrs: "CharacterAttribute") -> None:
        for ch in self.children:
            if isinstance(ch, Attribute):
                ch(attrs.copy())
            else:
                attrs.to_string(ch)

    def __neg__(self) -> "Attribute":
        result = _OtherAttr("", False)
        result.children.extend(self.children)
        return result

    def __repr__(self) -> str:
        return f"Attribute({self.children!r})"


class _NormalAttr(_Attribute):
    def __call__(self, attrs: "CharacterAttribute") -> None:
        attrs.__init__()
        super().__call__(attrs)


class _OtherAttr(_Attribute):
    def __init__(self, attrname: str, attrvalue: bool):
        self.attrname = attrname
        self.attrvalue = attrvalue

    def __call__(self, attrs: "CharacterAttribute") -> None:
        attrs = attrs.wantOne(**{self.attrname: self.attrvalue})
        super().__call__(attrs)


class _ColorAttr(_Attribute):
    def __init__(self, color: str, ground: str):
        self.color = color
        self.ground = ground

    def __call__(self, attrs: "CharacterAttribute") -> None:
        attrs = attrs.wantOne(**{self.ground: self.color})
        super().__call__(attrs)


class _ForegroundColorAttr(_ColorAttr):
    def __call__(self, attrs: "CharacterAttribute") -> None:
        super().__call__(attrs)


class _BackgroundColorAttr(_ColorAttr):
    def __call__(self, attrs: "CharacterAttribute") -> None:
        super().__call__(attrs)


class CharacterAttribute:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._attributes = helper.CharacterAttribute()

    def to_string(self, char: str) -> None:
        self._attributes.toVT102()
        print(char, end="")

    def copy(self) -> "CharacterAttribute":
        attrs = CharacterAttribute()
        attrs._attributes = self._attributes.copy()
        return attrs

    def wantOne(self, **kwargs: Any) -> "CharacterAttribute":
        attrs = CharacterAttribute()
        attrs._attributes = self._attributes.wantOne(**kwargs)
        return attrs


class Attribute:
    class _ColorAttribute:
        def __init__(self, ground: str):
            self.ground = ground

