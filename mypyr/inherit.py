from .type_check import TypeCheckError
from typing import Callable, Type, Union
from functools import wraps
from inspect import isfunction, isclass

def inherit(*cls: Type, errors=(TypeCheckError,NotImplementedError)) -> Callable:
    """A decorator which automatically wraps the underlying function and instead calls a parent class

    Args:
        cls : The parent class to inherit the function implementation from

    Example:
        A basic example of a class inheriting a method from a different class

        >>> class Parent:
        ...     def test(self,value):
        ...         return value + ">Parent"
        ...
        >>> class Child(Parent):
        ...     @inherit(Parent)
        ...     def test(self,value): ...
        ...

        Calling the 'test' method  from 'Child' results in:

        >>> obj = Child()
        >>> obj.test("Child")
        Child>Parent

        Note that the child class does NOT need to inherit from the parent class; however, it is generally recommended

    Raises:
        TypeError: If `cls` is not a class
        NotImplementedError: When the decorated function is called if no method can be found

    TODO:
        Handle annotations
    """
    if not all(isclass(c) for c in cls):
        raise TypeError("@inherit(*cls: Type) requires classes/objects as the arguments")

    # Define the decorator to return
    def decorator(func):
        funcs = [getattr(c,func.__name__) for c in cls if hasattr(c,func.__name__)]

        @wraps(func)
        def wrapper(*args,**kwargs):
            for f in funcs:
                try:
                    return f(*args,**kwargs)
                except errors:
                    pass
            raise NotImplementedError("could not find valid @inherit function for '"+funcs[0].__qualname__+"'")

        return wrapper
    return decorator