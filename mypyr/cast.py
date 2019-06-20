import re
from typing import Iterable, Any, Type
from infix import make_infix

# Map of Classes/Modules to functions which MIGHT convert them
AUTOMATIC_CONVERSIONS = {
    re: re.compile
}

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
    if cls is Any or isinstance(obj,cls):
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
    for k,v in AUTOMATIC_CONVERSIONS.items():
        if cls==k:
            return v(obj)
        try:
            if issubclass(cls,k):
                return v(obj)
        except TypeError:
            pass

    # If the class we have is castable, it may accept the object in its __init__ (especially if it's typed/overloaded)
    # This is a bit risky, but we're assuming we're only casting to well-behaving objects
    try:
        return cls(obj)
    except:
        pass

    # We've run out of things to try
    raise NotImplementedError('cannot convert object {obj!r} to {typ!r}'.format(obj=str(obj),typ=str(cls)))

# Use the infix package to allow this to be used lie
@make_infix('sub','rshift')
def to(obj, cls):
    """Attempt to cast an object to a desired type.
    The mirror-image of cast. Cast an object to type

    Infixed for the format '-to>>' making the following equivalent
        to(5.1,str)     == '5.1'
        (5.1 -to>> str) == '5.1'
    Be careful with the latter format as -to>> uses subtraction and bitwise shift operators
    which are in the middle of operator precedence and lower than things like multiplication!

    Args:
        obj: An object to be cast
        cls: Type to cast to

    Returns:
        The object cast to the target class
    """
    return cast(cls,obj)

# Monkey-patch to get rid of the extra bindings we don't want
def _infix_error(self,other): raise TypeError("unsupported infix format, use '-to>>'")
to.__class__.__rlshift__ = _infix_error
to.__class__.__sub__ = _infix_error
to.rbind.__rlshift__ = _infix_error
to.lbind.__sub__ = _infix_error
