from .type_check import TypeCheckError
from .overload import OMeta, overload
from .types import Function
from typing import Type
from functools import wraps
from inspect import isfunction

def inherit(*args,errors=(TypeCheckError,NotImplementedError)):
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
        ...

        Calling the 'test' method  from 'Child' results in:

        >>> obj = Child()
        >>> obj.test("Child")
        Child>Parent

        It is also possible to write Child as:
        ... class Child:
        ...     @inherit(Parent)
        ...     def test(self,value): ...
        ...

        Which is functionally identical for the method `test` while no other methods from `Parent` would be inherited.

        Note that the child class does NOT need to inherit from the parent class; however, it is generally recommended

    Raises:
        TypeError: If `cls` is not a class
        NotImplementedError: When the `@inherit` decorated function is called and no method can be found

    TODO:
        Handle annotations
    """
    _bases = []
    _funcs = []
    _errors = errors
    _wrapped = []

    # Define the wrapper for the function
    def wrapper(*args,**kwargs):
        for f in _funcs:
            print(_funcs)
            try:
                return f(*args,**kwargs)
            except errors:
                pass
        raise NotImplementedError("could not find valid @inherit method for "+_wrapped[0].__qualname__)

    # Define a followup script to populate bases if not known
    def followup(current, bases, **kwargs):
        print(bases,current)
        if len(_bases)==0:
            _bases.extend(bases)
        _funcs.extend([getattr(b,_wrapped[0].__name__) for b in _bases if hasattr(b,_wrapped[0].__name__)])
        print(_funcs)
        del current.__followup__

        return current

    # Assign the followup script to the wrapper
    wrapper.__followup__ = followup

    # Create a decorator for the function
    def decorator(func: Function):
        res = wraps(func)(wrapper)
        res.__followup__ = followup
        _wrapped.append(func)
        return res

    # If it's being called to decorate a function
    if len(args)==1 and isfunction(args[0]):
        return decorator(*args)

    # If it's being called with bases and/or errors defined
    elif all(isinstance(a,Type) for a in args):
        _bases.extend(args)
        return decorator

    # If it's being called with invalid arguments
    else:
        raise TypeError("invalid usage of @inherit")





