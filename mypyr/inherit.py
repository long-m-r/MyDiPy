from functools import wraps
from typing import Callable, Type

def inherit(cls: Type) -> Callable:
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
    """
    # Manually type check here. It'll be faster than decorator and is really easy here (Don't tell anyone)
    if not issubclass(cls,Type):
        raise TypeError("inherit decorator requires a class/object as the argument")

    def wrapper(func: Callable) -> Callable:
        # Do the lookup now so we can point straight to the function later
        pfunc = getattr(pclass,func.__name__)

        # Our parent function needs to be wrapped in another function so we don't overwrite the parent annotations
        @wraps(func)
        def fexec(*args,**kwargs):
            return pfunc(*args,**kwargs)

        # Update annotations before returning
        for k,v in pfunc.__annotations__.items():
            if k not in fexec.__annotations__:
                fexec.__annotations__[k]=v

        return fexec
    return wrapper