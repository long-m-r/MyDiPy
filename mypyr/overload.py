from .type_check import type_check, TypeCheckError
from inspect import isfunction
from functools import wraps
# from typing import Callable, Type
from collections import defaultdict as ddict

from typing import Callable, Iterable

def _merge_annotations(curr,new):
    # Merge annotations by items in new
    for k,v in new.__annotations__.items():
        # Get a set of the annotations
        nv = set(v) if isinstance(v,Iterable) else set([v])

        ov = curr.__annotations__.get(k,[])

        # Merge existing annotations with new ones
        nv |= set(ov) if isinstance(ov,Iterable) else set([ov])

        # Apply
        curr.__annotations__[k] = tuple(nv)

    # Merge docstrings as well, if there are any
    if new.__doc__ is not None:
        if curr.__doc__ is None:
            curr.__doc__ = new.__doc__
        else:
            curr.__doc__ += "\n\n"+new.__doc__

class _overload_dict(dict):
    """Private function. Don't use directly."""
    # Used in `OverloadableMeta.__prepare__(...)`
    #
    # Creates a dictionary which will automatically create an overloaded
    # function when `@overload` decorated functions or auto_overload=True
    # are overwritten (added to the dictionary 2+ times)

    def __init__(self,*args,**kwargs):
        # Create local dictionary to store our overloads
        self._overloads={}

        # Flag to see if only overloading `@overload` functions or all multiply defined functions
        self._auto_overload=kwargs.pop('auto_overload',False)

        # Initialize normally
        super().__init__(*args,**kwargs)

    def __setitem__(self,key,val):
        if isfunction(val) and key in self and isfunction(self[key]):
            # We only need to check functions for overloadedness if there's already one defined

            # Flag indicating if the new function should be overloaded
            oflag = getattr(val,'__overload__',self._auto_overload)

            if key in self._overloads and oflag:
                # It's already been overloaded, simply add to end and exit
                self._overloads[key].append(type_check(val))

                # Update the annotations/docstrings
                _merge_annotations(self[key],val)

                # Leave without actually changing the value
                return
            elif oflag and getattr(self[key],'__overload__',self._auto_overload):
                # We've got ourselves some brand new overloaded functions

                # List of functions to try
                funcs = [type_check(self[key]),type_check(val)]
                self._overloads[key] = funcs

                # Wrapper method which tries them in series
                @wraps(self[key])
                def wrapper(*args,**kwargs):
                    for f in funcs:
                        try:
                            return f(*args,**kwargs)
                        except TypeCheckError:
                            pass
                    raise NotImplementedError("could not find valid @overload function for '"+funcs[0].__qualname__+"'")
                wrapper.__typed__ = True

                # Update the annotations/docstrings
                _merge_annotations(wrapper,val)
                # Change the value we want in the dictionary
                val = wrapper

        # Go ahead and set the item in the dictionary
        super().__setitem__(key,val)

class OverloadableMeta(type):
    def __prepare__(name, bases, **kwds):
        # Dictionary that handles @overload methods intelligently
        auto_overload=kwds.pop('auto_overload',False)
        return _overload_dict(auto_overload=auto_overload)

    def __new__(metacls, name, bases, namespace, **kwds):
    #     # We need to look for @inherit tags
    #     for k,v in namespace.items():
    #         if getattr(v,'__overloaded__',False):
    #             for f in v.__functions__:
    #                 if getattr(f,'__inherits__',False) == [Ellipsis]:
    #                     f.__inherits__.remove(Ellipsis)
    #                     for b in bases:
    #                         if hasattr(b,f.__name__):
    #                             f.__inherits__.append(b)
    #         elif getattr(v,'__inherits__',False) == [Ellipsis]:
    #             v.__inherits__.remove(Ellipsis)
    #             for b in bases:
    #                 if hasattr(b,v.__name__):
    #                     v.__inherits__.append(b)

        return type.__new__(metacls, name, bases, namespace)

class OverloadableObject(metaclass=OverloadableMeta):
    pass

def overload(func):
    func.__overload__=True
    return func

# Aliases
OMeta=OverloadableMeta
OObject = OverloadableObject
