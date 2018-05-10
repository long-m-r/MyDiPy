from functools import wraps
from typing import Callable, Type
from collections import defaultdict as ddict
from .requiretype import requiretype

_overload_library=ddict(lambda: (list(), ddict(set)))

def overload(func: Callable) -> Callable:
    """A decorator which allows a class method to be defined multiple times to
    accept different data types for both arguments and return values.
    Iterates through the overloaded methods and identifies the FIRST instance
    whose parameters AND types match the passed arguments

    Args:
        func : A method or function to overload.

    Example:
        A basic example of an overloaded function:

        >>> @overload
        ... def a(i: int) -> str: return "Integer"
        ...
        >>> @overload
        ... def a(i: str): return "String"
        ...
        >>> @overload
        ... def a(i: int) -> int: return 1
        ...
        >>> a(0)
        'Integer'
        >>> a(0,_returns=int)
        1
        >>> a("test")
        'String'
        >>> a("test",_returns=str)
        TypeError: unable to find a valid overloaded function
        >>> a(0.1)
        TypeError: unable to find a valid overloaded function

    Raises:
        TypeError: If no overloaded method can be found which matches the data types in a function call

    Note:
        Un-typed parameters are assumed to accept any type; however, no assumptions are made about the return types.
        If `_returns` is specified, only functions with correspondingly annotated return types will be matched.
    """
    if not isinstance(func,Callable):
        raise TypeError('Only functions and methods can be used with @overload')

    key = getattr(func,'__qualname__')
    newfunc = requiretype(func)

    # Add function and annotation to library
    _overload_library[key][0].append(newfunc)
    for k,v in func.__annotations__.items():
        if isinstance(v,tuple):
            _overload_library[key][1][k] |= set(v)
        else:
            _overload_library[key][1][k].add(v)

    # Get a local pointer from our global so the global can be cleaned later
    library=_overload_library[key]

    # Caller function
    @wraps(func)
    def call(*args,**kwargs):
        result = None

        # Loop through each function
        for f in library[0]:
            try:
                # Get the result
                result = f(*args,**kwargs)
            except TypeError as e:
                # The function didn't match
                pass
            else:
                # If it's ..., we want to perform a lookup to our inherited classes
                if result is Ellipsis:
                    # Look through each base and try to call the same function there
                    for base in args[0].__class__.__bases__:
                        try:
                            result = getattr(base,func.__name__)(*args,**kwargs)
                            break
                        except:
                            # We don't care why it didn't work
                            pass
                # If we have any other result, return it. We can optionally type-check here if we are really pedantic

                else:
                    return result

        # If we make it here, we've run out of options.
        raise TypeError("unable to find a valid overloaded function")

    # Annotate our function accordingly
    setattr(call,'__annotations__',{k:tuple(v) for k,v in _overload_library[key][1].items()})
    setattr(call,'__typed__',True)

    return call

def overloaded(cls : Type) -> Type:
    """A class decorator which cleans up the global library of overload functions.
    Highly recommended for any class which contain `@overload` methods.

    Args:
        cls : A class which contains `@overload` methods

    Note:
        The cls is passed back unchanged, but the global namespace is cleaned up.
    """
    if not isinstance(cls,Type):
        raise TypeError('Only classes can be used with @overloaded')

    keys=list(_overload_library.keys())
    for k in keys:
        if k.startswith(cls.__qualname__):
            del _overload_library[k]
    return cls