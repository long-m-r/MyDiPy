from .type_check import type_check, TypeCheckError
from inspect import isfunction
from functools import wraps
from collections import defaultdict as ddict
from typing import Iterable, Any, Type
from infix import or_infix as infix

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

                wrapper.__typed__ = True

                # Update the annotations/docstrings
                _merge_annotations(wrapper,val)
                # Change the value we want in the dictionary
                val = wrapper

        # Go ahead and set the item in the dictionary
        super().__setitem__(key,val)

@infix
def cast(cls: Type, obj):
    """Attempt to cast an object to a desired type.
    Format is identical to MyPy's cast function and should be compatible.

    If the object is already of the correct class, it is passed through.

    Args:
        cls: Type to cast to
        obj: An object to be cast

    Returns:
        The object cast to the target class
    """
    # If we are already done. Do nothing:
    if cls is Any:
        return obj
    elif isinstance(obj,cls):
        return obj

    # If we have an object which looks castable:
    if hasattr(obj,'__cast__'):
        # If it is typed, we can specify the return type which is what we want
        if getattr(obj.__cast__,'__typed__',False):
            return obj.__cast__(cls,_returns=cls)
        # If not, we'll just have to call it blindly and it can throw its own errors
        else:
            return obj.__cast__(cls)

    # List of built-in conversion functions which can throw their own errors
    classes = { # Class : Conversion function
                str : str,
                int : int
            }

    # TODO: Do we want to catch errors here and keep trying or just go for gold on the first hit? Same applies above to __cast__
    for k,v in classes.items():
        if issubclass(k,cls):
            return v(obj)

    # We've run out of things to try
    raise NotImplementedError('cannot convert object {obj!r} to {typ!r}'.format(obj=str(obj),typ=str(cls)))

@infix
def to(obj, cls):
    return cast(cls,obj)

class TypedMeta(type):
    """A metaclass where multiply-defined functions are automatically overloaded"""
    def __prepare__(name, bases, **kwds):
        # Dictionary that handles @overload methods intelligently
        return _overload_dict(bases=bases, **kwds)

    def __new__(metacls, name, bases, namespace, **kwds):
        obj = type.__new__(metacls, name, bases, namespace)
        setattr(obj, '__annotations__', getattr(obj, '__annotations__', {}))
        return obj

class TypedObject(metaclass=TypedMeta):
    def __setattr__(self, key, val):
        # if key in self.__annotations__ and not isinstance(val,self.__annotations__[key]):
        if not isinstance(val,self.__annotations__.get(key,object)):
            raise TypeError('cannot assign {val!r} to {key!r} which is of {typ!r}'.format(val=str(type(val)),typ=str(self.__annotations__.get(key,object)),key=self.__class__.__qualname__+'.'+key))
        super().__setattr__(key,val)

    def __cast__(self, cls) -> str:
        return self.__str__()
    def __cast__(self, cls) -> int:
        return self.__int__()
    def __cast__(self, cls) -> bool:
        return self.__nonzero__()
    def __cast__(self, cls):
        raise NotImplementedError('cannot convert \'{inst!r}\' of type {obj!r} to {typ!r}'.format(inst=self.__class__.__qualname__,obj=str(type(self)),typ=str(cls)))

# class OverloadableFunction:
#     __typed__ = True

#     def __init__(self):
#         self._funcs=[]

#     def __call__(self,*args,**kwargs):
#         for f in self.funcs:
#             try:
#                 return f(*args,**kwargs)
#             except TypeCheckError:
#                 pass
#         raise NotImplementedError("could not find valid @overload function for '"+funcs[0].__qualname__+"'")

#     def overload(self,func):
#         self._funcs.append(type_check(func))
#         _merge_annotations(self,func)
#         return self

def overload(func):
    func.__overload__=True
    return type_check(func)