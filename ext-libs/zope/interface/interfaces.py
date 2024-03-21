from __future__ import annotations

from zope.interface import Interface
from zope.interface.interface import Attribute

class IAttribute(Interface):
    """Attribute descriptors"""

    interface: Interface = Attribute('interface',
                                     'Stores the interface instance in which the '
                                     'attribute is located.')

class IDeclaration(ISpecification):
    """Interface declaration

    Declarations are used to express the interfaces implemented by
    classes or provided by objects.
    """

    def __contains__(self, interface: Interface) -> bool:
        """Test whether an interface is in the specification

        Return true if the given interface is one of the interfaces in
        the specification and false otherwise.
        """
        pass

    def __iter__(self) -> Iterator[Interface]:
        """Return an iterator for the interfaces in the specification
        """
        pass

    def flattened(self) -> Iterator[Interface]:
        """Return an iterator of all included and extended interfaces

        An iterator is returned for all interfaces either included in
        or extended by interfaces included in the specifications
        without duplicates. The interfaces are in "interface
        resolution order". The interface resolution order is such that
        base interfaces are listed after interfaces that extend them
        and, otherwise, interfaces are included in the order that they
        were defined in the specification.
        """
        pass

    def __sub__(self, interfaces: Union[Interface, IDeclaration]) -> IDeclaration:
        """Create an interface specification with some interfaces excluded

        The argument can be an interface or an interface
        specifications.  The interface or interfaces given in a
        specification are subtracted from the interface specification.

        Removing an interface that is not in the specification does
        not raise an error. Doing so has no effect.

        Removing an interface also removes sub-interfaces of the interface.

        """
        pass

    def __add__(self, interfaces: Union[Interface, IDeclaration]) -> IDeclaration:
        """Create an interface specification with some interfaces added

        The argument can be an interface or an interface
        specifications.  The interface or interfaces given in a
        specification are added to the interface specification.

        Adding an interface that is already in the specification does
        not raise an error. Doing so has no effect.
        """
        pass

    def __nonzero__(self) -> bool:
        """Return a true value of the interface specification is non-empty
        """
        pass

class IElement(Interface):
    """Objects that have basic documentation and tagged values.
    """

    __name__: str = Attribute('__name__', 'The object name')
    __doc__: str = Attribute('__doc__', 'The object doc string')

    def getTaggedValue(self, tag: str) -> Any:
        """Returns the value associated with `tag`.

        Raise a `KeyError` of the tag isn't set.
        """
        pass

    def queryTaggedValue(self, tag: str, default: Any = None) -> Any:
        """Returns the value associated with `tag`.

        Return the default value of the tag isn't set.
        """
        pass

    def getTaggedValueTags(self) -> List[str]:
        """Returns a list of all tags.
        """
        pass

    def setTaggedValue(self, tag: str, value: Any) -> None:
        """Associates `value` with `key`.
        """
        pass

class IInterface(ISpecification, IElement):
    """Interface objects

    Interface objects describe the behavior of an object by containing
    useful information about the object.  This information includes:

      o Prose documentation about the object.  In Python terms, this
        is called the "doc string" of the interface.  In this element,
        you describe how the object works in prose language and any
        other useful information about the object.

      o Descriptions of attributes.  Attribute descriptions include
        the name of the attribute and prose documentation describing
        the attributes usage.

      o Descriptions of methods.  Method descriptions can include:

        - Prose "doc string" documentation about the method and its
          usage.

        - A description of the methods arguments; how many arguments
          are expected, optional arguments and their default values,
          the position or arguments in the signature, whether the
          method accepts arbitrary arguments and whether the method
          accepts arbitrary keyword arguments.

      o Optional tagged data.  Interface objects (and their attributes and
        methods) can have optional, application specific tagged data
        associated with them.  Examples uses for this are examples,
        security assertions, pre/post conditions, and other possible
        information you may want to associate with an Interface or its
        attributes.

    Not all of this information is mandatory.  For example, you may
    only want the methods of your interface to have prose
    documentation and not describe the arguments of the method in
    exact detail.  Interface objects are flexible and let you give or
    take any of these components.

    Interfaces are created with the Python class statement using
    either Interface.Interface or another interface, as in::

      from zope.interface import Interface

      class IMyInterface(Interface):
        '''Interface documentation'''

        def meth(arg1, arg2):
            '''Documentation for meth'''

        # Note that there is no self argument

     class IMySubInterface(IMyInterface):
        '''Interface documentation'''

        def meth2():
            '''Documentation for meth2'''

    You use interfaces in two ways:

    o You assert that your object implement the interfaces.

      There are several ways that you can assert that an object
      implements an interface:

      1. Call zope.interface.im
