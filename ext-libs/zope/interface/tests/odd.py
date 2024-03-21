##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Odd meta class that doesn't subclass type.

This is used for testing support for ExtensionClass in new interfaces.

  >>> class A(object):
  ...     __metaclass__ = MetaClass
  ...     a = 1
  ...
  >>> A.__name__
  'A'
  >>> A.__bases__ == (object,)
  True
  >>> class B(object):
  ...     __metaclass__ = MetaClass
  ...     b = 1
  ...
  >>> class C(A, B): pass
  ...
  >>> C.__name__
  'C'
  >>> int(C.__bases__ == (A, B))
  1
  >>> a = A()
  >>> aa = A()
  >>> a.a
  1
  >>> aa.a
  1
  >>> aa.a = 2
  >>> a.a
  1
  >>> aa.a
  2
  >>> c = C()
  >>> c.a
  1
  >>> c.b
  1
  >>> c.b = 2
  >>> c.b
  2
  >>> C.c = 1
  >>> c.c
  1
  >>> import sys
  >>> if sys.version[0] == '2': # This test only makes sense under Python 2.x
  ...     from types import ClassType
  ...     assert not isinstance(C, (type, ClassType))
  
  >>> int(C.__class__.__class__ is C.__class__)
  1

"""

class MetaMetaClass(type):

    def __getattribute__(self, name):
        if name == '__class__':
            return self
        return type.__getattribute__(self, name)
    

class MetaClass(object, metaclass=MetaMetaClass):
    """Odd classes
    """

    def __init__(self, name, bases, namespace):
        self.__name__ = name
        self.__bases__ = bases
        self.__dict__.update(namespace)

    def __call__(self):
        return OddInstance(self)

    def __getattr__(self, name):
        for b in self.__bases__:
            v = getattr(b, name, self)
            if v is not self:
                return v
        raise AttributeError(name)

    def __repr__(self):
        return "<odd class %s at %s>" % (self.__name__, hex(id(self)))

class OddInstance(object):

    def __init__(self, cls):
        self.__class__ = cls

    def __getattribute__(self, name):
        dict_ = object.__getattribute__(self, '__dict__')
        if name == '__dict__':
            return dict_
        v = dict_.get(name)
        if v is not None:
            return v
        return getattr(type(self), name)

    def __setattr__(self, name, value):
        dict_.__setitem__(self, name, value)

    def __delattr__(self, name):
        if name in dict_:
            dict_.__delitem__(self, name)
        else:
            super().__delattr__(name)

    def __repr__(self):
        return "<odd %s instance at %s>" % (
            self.__class__.__name__, hex(id(self)))

if __name__ == "__main__":
    import doctest, __main__
    doctest.testmod(__main__, isprivate=lambda *a: False)
