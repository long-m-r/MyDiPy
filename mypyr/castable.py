from typing import Type
from .overload import overload, overloaded

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
    if isinstance(obj,cls):
        return obj

    # If we have an object which looks castable:
    if hasattr(obj,'__cast__'):
        # TODO: should we check __casttypes__? Can save execution time but if there is an undefined output catch-all we would never try it. I don't think we want to do this.
        # if hasattr(obj,'__casttypes__') and c in obj.__casttypes__:
            # return obj.__cast__(cls,_returns=cls)

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

@overloaded
class castable(object):
    @overload
    def __cast__(self, cls: Type) -> str:
        return self.__str__()
    @overload
    def __cast__(self, cls: Type):
        raise TypeError('cannot convert object {inst!r} to {typ!r}'.format(inst=str(self),typ=str(cls)))

    @property
    def __casttypes__(self) -> tuple:    return self.__cast__.__annotations__['return']