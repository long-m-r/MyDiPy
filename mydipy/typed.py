from .type_check import type_check, TypeCheckError
from inspect import isfunction
from functools import wraps
from collections import defaultdict as ddict
from typing import Iterable, Any, Type

def _merge_annotations(curr,new):
    """
    Private function. Don't use directly.

    This function will modify the annotations
    and docstring of `curr` to incorporate those
    in `new`
    """
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
    """
    Private class. Don't use directly.

    Used in `OverloadableMeta.__prepare__(...)`

    Creates a dictionary which will automatically create an overloaded
    function when `@overload` decorated functions or auto_overload=True
    are overwritten (added to the dictionary 2+ times)
    """

    def __init__(self,*args,**kwargs):
        # Create local dictionary to store our overloads
        self._overloads={}
        # Flag to see if only overloading `@overload` functions or all multiply defined functions
        self._auto_overload=kwargs.pop('auto_overload',True)
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
                    # funcs is a pointer so as we append it'll pick up the later ones
                    for f in funcs:
                        # Check if this function annotations match
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

class TypedMeta(type):
    """
    A metaclass where function my be overloaded and executed with multiple dispatch.

    Generally one should inherit from OverloadObject unless there is a specific
    reason for not doing so (e.g., not having casting functionality)

    Args:
        auto_overload:
            When inheriting from this metaclass, the

    Example:
        >>> class Example(metaclass=TypedMeta):
        ...     def a(self, val : int) -> str:
        ...         return 'int'
        ...     def a(self, val : str) -> str:
        ...         return 'str'
        ...
        >>> ex = Example()
        >>> print(ex.a('test'))
        str
        >>> print(ex.a(1))
        int
    """
    def __prepare__(name, bases, **kwds):
        # Dictionary that handles @overload methods intelligently
        return _overload_dict(bases=bases, **kwds)

    def __new__(metacls, name, bases, namespace, **kwds):
        obj = type.__new__(metacls, name, bases, namespace)
        # Create empty annotations if they don't exist
        setattr(obj, '__annotations__', getattr(obj, '__annotations__', {}))
        return obj

# class TypedObject(metaclass=TypedMeta):
#     pass

class OverloadObject(metaclass=TypedMeta):
    """
    An object allowing multiply defined functions to be overloaded


    You should generally inherit from this object if you want to have overloading
    and multiple dispatch, as well as support for targeted inheritance and casting
    as provided by other parts of this module.

    Args:
        auto_overload : whether to automatically overload (true) or only when the `@overload` decorator is used. Default True

    Example:
        >>> class A(OverloadObject):
        ...     def test(self, val: str) -> str:
        ...         return "Value="+self.str
        ...
        ...     def test(self, val: int) -> int:
        ...         return -val
        ...
        ...     def test(self, val):
        ...         raise ValueError()
        ...
        >>> ex = A()
        >>> print(ex.test(1))
        -1
        >>> print(ex.test(1,_returns=str))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        ValueError
        >>> print(ex.test('test'))
        Value=test
    """

    def __setattr__(self, key, val):
        # if key in self.__annotations__ and not isinstance(val,self.__annotations__[key]):
        if not isinstance(val,self.__annotations__.get(key,object)):
            raise TypeError('cannot assign {val!r} to {key!r} which is of {typ!r}'.format(
                val=str(type(val)),
                typ=str(self.__annotations__.get(key,object)),
                key=self.__class__.__qualname__+'.'+key)
            )
        super().__setattr__(key,val)

    def __cast__(self) -> str:
        """Cast function to str"""
        return self.__str__()
    def __cast__(self) -> int:
        """Cast function to int"""
        return self.__int__()
    def __cast__(self) -> bool:
        """Cast function to bool"""
        return self.__nonzero__()
    def __cast__(self):
        """Cast function to throw an error for all other types"""
        raise NotImplementedError('cannot convert \'{inst!r}\' of type {obj!r} to {typ!r}'.format(inst=self.__class__.__qualname__,obj=str(type(self)),typ=str(cls)))

class OverloadFunction:
    """
    A decorator class allowing functions to be overloaded.

    Example:
        >>> @OverloadFunction
        ... def test(a: str):
        ...     return 'String'
        ...
        >>> @test.overload
        ... def test(a: int):
        ...     return 'Integer'
    """
    __typed__ = True

    def __init__(self,func):
        """
        Use the constructor as a decorator (@OverloadableFunction)

        Args:
            func : A function to allow to be overloaded
        Returns:
            OverloadFunction instance which behaves like a function
        """
        self._funcs=[type_check(func)]

    def __call__(self,*args,**kwargs):
        for f in self.funcs:
            try:
                return f(*args,**kwargs)
            except TypeCheckError:
                pass
        raise NotImplementedError("could not find valid @overload function for '"+funcs[0].__qualname__+"'")

    def overload(self,func):
        """
        Add another overload definition to the current function

        Args:
            func : A function to append to the overload list
        Returns:
            The combined function with multiple dispatch
        """
        self._funcs.append(type_check(func))
        _merge_annotations(self,func)
        return self

def overload(func):
    """
    Overload decorator for class methods where auto_overload=False.

    If using this, use @overload for every entry for any methods which are multiply
    defined.

    Args:
        func : A function to make overloadable (or to append to an existing overload)
    Returns:
        The same function with type checking and overloading enabled
    Example:
        The following two classes are functionaliy identical and
        highlights the usage of this decorator:

        >>> class ExampleAutoOverload(metaclass=TypedMeta):
        >>>     def a(self, val : int) -> str:
        >>>         return 'int'
        >>>     def a(self, val : str) -> str:
        >>>         return 'str'
        >>>
        >>> class ExampleWithDecorator(metaclass=TypedMeta,auto_overload=False):
        >>>     @overload
        >>>     def a(self, val : int) -> str:
        >>>         return 'int'
        >>>     @overload
        >>>     def a(self, val : str) -> str:
        >>>         return 'str'
    """
    func.__overload__ = True
    return type_check(func)