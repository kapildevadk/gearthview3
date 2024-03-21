# -*- test-case-name: twisted.web.test.test_template -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from zope.interface import implements
from typing import Any, Callable, List, Optional

from twisted.web.iweb import IRenderable
from twisted.web.error import MissingRenderMethod, UnexposedMethodError
from twisted.web.error import MissingTemplateLoader


class Expose:
    """
    Helper for exposing methods for various uses using a simple decorator-style
    callable.

    Instances of this class can be called with one or more functions as
    positional arguments.  The names of these functions will be added to a list
    on the class object of which they are methods.

    @ivar attributeName: The attribute with which exposed methods will be
    tracked.
    """
    __slots__ = ('doc', 'exposed')

    def __init__(self, doc: Optional[str] = None):
        self.doc = doc
        self.exposed = []

    def __call__(self, *funcObjs: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """
        Add one or more functions to the set of exposed functions.

        This is a way to declare something about a class definition, similar to
        L{zope.interface.implements}.  Use it like this::

            magic = Expose('perform extra magic')
            class Foo(Bar):
                def twiddle(self, x, y):
                    ...
                def frob(self, a, b):
                    ...
                magic(twiddle, frob)

        Later you can query the object::

            aFoo = Foo()
            magic.get(aFoo, 'twiddle')(x=1, y=2)

        The call to C{get} will fail if the name it is given has not been
        exposed using C{magic}.

        @param funcObjs: One or more function objects which will be exposed to
        the client.

        @return: The first of C{funcObjs}.
        """
        if not funcObjs:
            raise TypeError("expose() takes at least 1 argument (0 given)")
        for fObj in funcObjs:
            if fObj in self.exposed:
                continue
            fObj.exposedThrough = getattr(fObj, 'exposedThrough', [])
            fObj.exposedThrough.append(self)
        self.exposed.extend(funcObjs)
        return funcObjs[0]

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return self.get(name)

    def get(self, instance: Any, methodName: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve an exposed method with the given name from the given instance.

        @raise UnexposedMethodError: Raised if C{default} is not specified and
        there is no exposed method with the given name.

        @return: A callable object for the named method assigned to the given
        instance.
        """
        method = getattr(instance, methodName, None)
        exposedThrough = getattr(method, 'exposedThrough', [])
        if self not in exposedThrough:
            if default is self._nodefault:
                raise UnexposedMethodError(self, methodName)
            return default
        return method

    @classmethod
    def _withDocumentation(cls, thunk: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """
        Slight hack to make users of this class appear to have a docstring to
        documentation generators, by defining them with a decorator.  (This hack
        should be removed when epydoc can be convinced to use some other method
        for documenting.)
        """
        return cls(thunk.__doc__)


# Avoid exposing the ugly, private classmethod name in the docs.  Luckily this
# namespace is private already so this doesn't leak further.
exposer = Expose._withDocumentation

@exposer
def renderer() -> Callable[[Any], Any]:
    """
    Decorate with L{renderer} to use methods as template render directives.

    For example::

        class Foo(Element):
            @renderer
            def twiddle(self, request, tag):
                return tag('Hello, world.')

        <div xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1">
            <span t:render="twiddle" />
        </div>

    Will result in this final output::

        <div>
            <span>Hello, world.</span>
        </div>
    """


class Element:
    """
    Base for classes which can render part of a page.

    An Element is a renderer that can be embedded in a stan document and can
    hook its template (from the loader) up to render methods.

    An Element might be used to encapsulate the rendering of a complex piece of
    data which is to be displayed in multiple different contexts.  The Element
    allows the rendering logic to be easily re-used in different ways.

    Element returns render methods which are
