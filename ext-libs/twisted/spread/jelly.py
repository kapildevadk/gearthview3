# -*- test-case-name: twisted.test.test_jelly -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
S-expression-based persistence of Python objects.

This module provides functions to serialize and deserialize Python objects to
and from s-expressions. It is similar to the `pickle` module but aims for
security, human readability, and portability to other environments.

@author: Glyph Lefkowitz
"""

import sys
import warnings
from types import (
    StringType,
    UnicodeType,
    IntType,
    TupleType,
    ListType,
    LongType,
    FloatType,
    FunctionType,
    MethodType,
    ModuleType,
    DictionaryType,
    InstanceType,
    NoneType,
    ClassType,
)
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zope.interface import Interface

    from twisted.spread.interfaces import IJellyable, IUnjellyable
else:
    Interface = object

    class IJellyable(Interface):
        pass

    class IUnjellyable(Interface):
        pass

DictTypes = (DictionaryType,)

None_atom = "None"  # N
class_atom = "class"  # c
module_atom = "module"  # m
function_atom = "function"  # f

# references
dereference_atom = 'dereference'  # D
persistent_atom = 'persistent'  # p
reference_atom = 'reference'  # r

# mutable collections
dictionary_atom = "dictionary"  # d
list_atom = 'list'  # l
set_atom = 'set'

# immutable collections
#   (assignment to __dict__ and __class__ still might go away!)
tuple_atom = "tuple"  # t
instance_atom = 'instance'  # i
frozenset_atom = 'frozenset'

# errors
unpersistable_atom = "unpersistable"  # u

_set = set
_sets = None

try:
    warnings.filterwarnings("ignore", category=DeprecationWarning,
                            message="the sets module is deprecated", append=True)
    import sets as _sets
finally:
    warnings.filters.pop()


def _newInstance(cls, state: Optional[Dict[str, Any]] = None) -> Any:
    """
    Make a new instance of a class without calling its __init__ method.

    Supports both new- and old-style classes.

    @param state: A dict used to update inst.__dict__ or None to skip this
        part of initialization.

    @return: A new instance of cls.
    """
    if not isinstance(cls, Type):
        # new-style
        inst = cls.__new__(cls)

        if state is not None:
            inst.__dict__.update(state)  # Copy 'instance' behaviour
    else:
        if state is not None:
            inst = InstanceType(cls, state)
        else:
            inst = InstanceType(cls)
    return inst


def _maybeClass(classnamep):
    try:
        object
    except NameError:
        isObject = 0
    else:
        isObject = isinstance(classnamep, type)
    if isinstance(classnamep, ClassType) or isObject:
        return qual(classnamep)
    return classnamep


def setUnjellyableForClass(classname, unjellyable):
    """
    Set which local class will represent a remote type.

    If you have written a Copyable class that you expect your client to be
    receiving, write a local "copy" class to represent it, then call::

        jellier.setUnjellyableForClass('module.package.Class', MyCopier).

    Call this at the module level immediately after its class
    definition. MyCopier should be a subclass of RemoteCopy.

    The classname may be a special tag returned by
    'Copyable.getTypeToCopyFor' rather than an actual classname.

    This call is also for cached classes, since there will be no
    overlap.  The rules are the same.
    """
    global unjellyableRegistry
    classname = _maybeClass(classname)
    unjellyableRegistry[classname] = unjellyable
    globalSecurity.allowTypes(classname)


def setUnjellyableFactoryForClass(classname, copyFactory):
    """
    Set the factory to construct a remote instance of a type::

      jellier.setUnjellyableFactoryForClass('module.package.Class', MyFactory)

    Call this at the module level immediately after its class definition.
    C{copyFactory} should return an instance or subclass of
    L{RemoteCopy<pb.RemoteCopy>}.

    Similar to L{setUnjellyableForClass} except it uses a factory instead
    of creating an instance.
    """
    global unjellyableFactoryRegistry
    classname = _maybeClass(classname)
    unjellyableFactoryRegistry[classname] = copyFactory
    globalSecurity.allowTypes(classname)


def setUnjellyableForClassTree(module, baseClass, prefix=None):
    """
    Set all classes in a module derived from C{baseClass} as copiers for
    a corresponding remote class.

    When you have a heirarchy of Copyable (or Cacheable) classes on one
    side, and
