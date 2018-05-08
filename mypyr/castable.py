from typing import Type
from .overload import overload, overloaded

def cast(cls: Type, inst):
    # If we are already done. Do nothing (HALLELUJAH!):
    if isinstance(inst,cls):
        return inst
    
    # If we have an object which looks castable:
    if hasattr(inst,'__cast__'):
        # TODO: should we check __casttypes__? Can save execution time but if there is an undefined output catch-all we would never try it. I don't think we want to do this.
        # >> I think the mypy linter should discover this sort of issue (maybe)
        # if hasattr(inst,'__casttypes__') and c in inst.__casttypes__:
            # return inst.__cast__(cls,_returns=cls)
        
        # If it is typed, we can specify the return type which is what we want
        if getattr(inst.__cast__,'__typed__',False):
            return inst.__cast__(cls,_returns=cls)
        # If not, we'll just have to call it blindly and it can throw its own errors
        else:
            return inst.__cast__(cls)
    
    # List of built-in conversion functions which can throw their own errors
    classes = { # Class : Conversion function
                str : str
                int : str
            }

    # We can't assume the cls is actually a key (e.g., it could be Iterator) so we need to do issubclass on each
    # TODO: Do we want to catch errors here and keep trying or just go for gold on the first hit? Same applies above to __cast__
    for k,v in classes.items():
        if issubclass(k,cls):
            return v(inst)

    # We've run out of things to try
    raise TypeError('cannot convert object {inst!r} to {typ!r}'.format(inst=str(inst),typ=str(cls)))

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