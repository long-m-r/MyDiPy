from .type_check import TypeCheckError
from .overload import overload, OverloadableMeta
from .inherit import inherit
from typing import Type, Any

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
    # If we are already done. Do nothing (HALLELUJAH!):
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

    # We can't assume the cls is actually a key (e.g., it could be Iterator) so we need to do issubclass on each
    # TODO: Do we want to catch errors here and keep trying or just go for gold on the first hit? Same applies above to __cast__
    for k,v in classes.items():
        if issubclass(k,cls):
            return v(obj)

    # We've run out of things to try
    raise TypeError('cannot convert object {obj!r} to {typ!r}'.format(obj=str(obj),typ=str(cls)))

class CastError(TypeError,NotImplementedError): pass

class CastableMeta(OverloadableMeta):
    def __prepare__(name, bases, **kwds):
        kwds['auto_overload_dict']={'__cast__': True}
        return OverloadableMeta.__prepare__(name, bases, **kwds)

    def __new__(metacls, name, bases, namespace, **kwds):

        # @overload
        # @inherit(errors=TypeCheckError)
        # def __cast__(self, cls: Type): ...

        # namespace['__cast__'] = __cast__

        return OverloadableMeta.__new__(metacls, name, bases, namespace, **kwds)

class CastableObject(metaclass=CastableMeta):
    def __cast__(self, cls: Type) -> str:
        return self.__str__()
    def __cast__(self, cls: Type) -> bool:
        return self.__nonzero__()
    def __cast__(self, cls: Type) -> int:
        return self.__int__()
    def __cast__(self, cls: Type):
        raise CastError('cannot convert object {inst!r} to {typ!r}'.format(inst=str(self),typ=str(cls)))

# Aliases
CMeta = CastableMeta
CObject = CastableObject