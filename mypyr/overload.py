from functools import wraps
from typing import Callable, Type
from collections import defaultdict as ddict
from .requiretype import requiretype

_overload_library=ddict(lambda: (list(), ddict(set)))

def overload(func: Callable) -> Callable:
    # TODO: Is this key sufficiently unique? I'd prefer to store it in the class itself but that won't work with a single @overload decorator
    key = getattr(func,'__qualname__')

    # We absolutely need to do requiretypes to pick the correct method. Decorated.
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
        raise TypeError("unable to find a valid function")

    # Annotate our function accordingly
    setattr(call,'__annotations__',{k:tuple(v) for k,v in _overload_library[key][1].items()})
    setattr(call,'__typed__',True)

    return call

def overloaded(cls : Type) -> Type:
    print('Class '+cls.__qualname__)
    print(_overload_library)
    for k in _overload_library:
        if k.startswith(cls.__qualname__):
            del _overload_library[k]
    print(_overload_library)
    return cls