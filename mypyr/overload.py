from .type_check import type_check, TypeCheckError
from inspect import isfunction
from functools import wraps
from collections import defaultdict as ddict

from typing import Callable, Iterable

def _merge_annotations(curr,new):
    """Private function. Don't use directly."""
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
    """Private class. Don't use directly."""
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
        self._mapped_overloads = ddict(lambda: self._auto_overload, kwargs.pop('auto_overload_dict',{}))

        # Initialize normally
        super().__init__(*args,**kwargs)

    def __setitem__(self,key,val):
        if isfunction(val) and key in self and isfunction(self[key]):
            # We only need to check functions for overloadedness if there's already one defined

            # Flag indicating if the new function should be overloaded
            oflag = getattr(val,'__overload__',self._mapped_overloads[key])

            if key in self._overloads and oflag:
                # It's already been overloaded, simply add to end and exit
                self._overloads[key].append(type_check(val))

                # Update the annotations/docstrings
                _merge_annotations(self[key],val)

                # Leave without actually changing the value
                return
            elif oflag and getattr(self[key],'__overload__',self._mapped_overloads[key]):
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

                def followup(*args,**kwargs):
                    for i,f in enumerate(funcs):
                        fu = getattr(f,'__followup__',False)
                        if fu:
                            newkwargs = dict(kwargs)
                            newkwargs['current']=f
                            funcs[i]=fu(*args,**newkwargs)
                    return wrapper

                wrapper.__followup__=followup
                wrapper.__typed__ = True


                # Update the annotations/docstrings
                _merge_annotations(wrapper,val)
                # Change the value we want in the dictionary
                val = wrapper

        # Go ahead and set the item in the dictionary
        super().__setitem__(key,val)


class FollowupMeta(type):
    def __new__(metacls, name, bases, namespace, **kwds):
        # Check for any followup methods
        for k,v in namespace.items():
            if getattr(v,'__followup__',False):
                namespace[k] = v.__followup__(current=v, name=name, bases=bases, **kwds)
                # del v.__followup__

        # Call super w/out kwds
        return type.__new__(metacls, name, bases, namespace)

class OverloadableMeta(FollowupMeta):
    def __prepare__(name, bases, **kwds):
        # Dictionary that handles @overload methods intelligently
        return _overload_dict(**kwds)

    def __new__(metacls, name, bases, namespace, **kwds):
        # # Remove arguments for this class
        # kwds.pop('auto_overload_dict',{})
        # kwds.pop('auto_overload',False)

        return FollowupMeta.__new__(metacls, name, bases, dict(namespace), **kwds)

class OverloadableObject(metaclass=OverloadableMeta):
    pass

class OverloadableFunction:
    __typed__ = True

    def __init__(self):
        self._funcs=[]

    def __call__(self,*args,**kwargs):
        for f in self.funcs:
            try:
                return f(*args,**kwargs)
            except TypeCheckError:
                pass
        raise NotImplementedError("could not find valid @overload function for '"+funcs[0].__qualname__+"'")

    def overload(self,func):
        self._funcs.append(type_check(func))
        _merge_annotations(self,func)
        return self

def overload(func):
    func.__overload__=True
    return type_check(func)

# Aliases
FMeta = FollowupMeta
OMeta = OverloadableMeta
OObject = OverloadableObject
OFunc = OverloadableFunction