from .type_check import TypeCheckError, type_check
from .types import Function
from typing import Type
from functools import wraps
from inspect import isfunction

def inherit(*args,errors=(NotImplementedError)):
    """A decorator which automatically wraps the underlying function and instead calls a parent class
    The body of the wrapped function is entirely ignored.
    Annotations of the parent class will be applied to the wrapped function **unless** they are otherwise
    defined

    These functions are mostly useless until you start working with the Typed

    Args:
        cls : The parent class to inherit the function implementation from
        errors : An error or Tuple of errors which will, if encountered, cause the search to skip that method and continue

    Example:
        A basic example of a class inheriting a method from a different class

        >>> class Parent:
        ...     def test(self,value):
        ...         return value + ">Parent"
        ...
        >>> class Child(Parent):
        ...     @inherit
        ...     def test(self,value): ...
        >>> obj = Child()
        >>> obj.test("Child")
        Child>Parent

        It is also possible to write Child as:
        >>> class Child:
        ...     @inherit(Parent)
        ...     def test(self,value): ...

        Which is functionally identical for the method `test` while no other methods from `Parent` would be inherited.
        This is generally not recommended, but if your class inherits from multiple classes it may be useful to specify
        which one to inherit from.
    Raises:
        TypeError: If `cls` is not a class
        NotImplementedError: When the `@inherit` decorated function is called and no method can be found

    TODO:
        Handle annotations
    """
    bases = []
    funcs = []
    wrapped = []

    # Define the wrapper for the function
    def wrapper(*args,**kwargs):
        if len(bases)==0:
            # We don't have any bases, extract from the object
            bases.extend(args[0].__class__.__bases__)
            # funcs.extend([getattr(b,wrapped[0].__name__) for b in bases if hasattr(b,wrapped[0].__name__)])

        if len(funcs)==0:
            # Extract functions from the bases
            funcs.extend([type_check(getattr(b,wrapped[0].__name__)) for b in bases if hasattr(b,wrapped[0].__name__)])

        for f in funcs:
            try:
                return f(*args,**kwargs)
            except errors:
                pass
        raise TypeCheckError("could not find valid @inherit method for "+wrapped[0].__qualname__)

    wrapper.__inherit__ = True

    # Create a decorator for the function
    def decorator(func: Function):
        res = wraps(func)(wrapper)
        wrapped.append(func)
        return type_check(res)

    if len(args)==1 and isfunction(args[0]):
        # If it's being called to decorate a function
        return decorator(*args)
    elif all(isinstance(a,Type) for a in args):
        # If it's being called with bases and/or errors defined
        bases.extend(args)
        return decorator
    else:
        raise TypeError("invalid usage of @inherit")
