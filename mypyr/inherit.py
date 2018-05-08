from functools import wraps
from typing import Callable, Type

def inherit(pclass: Type) -> Callable:
    # Manually type check here. It'll be faster than decorator and is really easy here (Don't tell anyone)
    if not issubclass(pclass,object):
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