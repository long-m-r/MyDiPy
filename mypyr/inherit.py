from .type_check import TypeCheckError, type_check
from .types import Function
from typing import Type
from functools import wraps
from inspect import isfunction

def _filter(func):
    if getattr(func,'__typed__',False):
        return func

    def wrapper(*args,**kwargs):
        kwargs.pop("_returns",None)
        return func(*args,**kwargs)

    return wraps(func)(wrapper)

def inherit(*args,errors=TypeCheckError):
    """A decorator which automatically wraps the underlying function and instead calls a parent class

    Args:
        cls : The parent class to inherit the function implementation from
        errors : An error or Tuple of errors which will, if encountered, will cause the search to skip that method and continue

    Example:
        A basic example of a class inheriting a method from a different class

        >>> class Parent:
        ...     def test(self,value):
        ...         return value + ">Parent"
        ...
        >>> class Child(Parent):
        ...     @inherit
        ...     def test(self,value): ...

        Calling the 'test' method  from 'Child' results in:

        >>> obj = Child()
        >>> obj.test("Child")
        Child>Parent

        It is also possible to write Child as:

        ... class Child:
        ...     @inherit(Parent)
        ...     def test(self,value): ...

        Which is functionally identical for the method `test` while no other methods from `Parent` would be inherited.

        Note that the child class does NOT need to inherit from the parent class; however, it is generally recommended

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

        if len(funcs)==0:
            # Extract functions from the bases
            funcs.extend([type_check(getattr(b,wrapped[0].__name__)) for b in bases if hasattr(b,wrapped[0].__name__)])

        for f in funcs:
            try:
                return f(*args,**kwargs)
            except errors:
                pass
        raise NotImplementedError("could not find valid @inherit method for "+wrapped[0].__qualname__)

    # Create a decorator for the function
    def decorator(func: Function):
        res = wraps(func)(wrapper)
        res.__typed__=True
        wrapped.append(func)
        return res

    if len(args)==1 and isfunction(args[0]):
        # If it's being called to decorate a function
        return decorator(*args)
    elif all(isinstance(a,Type) for a in args):
        # If it's being called with bases and/or errors defined
        bases.extend(args)
        return decorator
    else:
        raise TypeError("invalid usage of @inherit")





