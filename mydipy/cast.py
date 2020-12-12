import re
from typing import Iterable, Any, Type
from infix import make_infix

# Map of Classes/Modules to functions which MIGHT convert them
AUTOMATIC_CONVERSIONS = {
    re: re.compile
}

def cast(cls: Type, obj):
    """
    Cast an object to a desired type via the `__cast__` magic method.

    The format of `cast` is identical to MyPy's cast function and should be compatible.
    If the object is already of the correct class, it is passed through.

    There is a mirror-image function `to` which also casts. It has an infix for `-to>>`

    Therefore, all three of these formats are identical:
        `cast(str,5.1) == to(5.1,str) == (5.1 -to>> str) == '5.1'`

    While the `-to>>` format is easy to read, be careful as subtraction and bitshift operators
    are in the middle of operator precedence. If using the infix, always use parentheses!

    Args:
        cls: Type to cast to
        obj: An object to be cast

    Returns:
        The object cast to the target class

    Raises:
        TypeError: If the class cannot be converted automatically

    Example:
        >>> a = OverloadObject()
        >>> cast(str, a) == str(a)
        True
        >>> cast(str, a) == a.__str__()
        True
    """
    # If we are already done. Do nothing:
    if cls is Any or type(obj) == cls:
        return obj

    # If we have an object which looks castable (intentionally not catching errors here as they may be desired)
    if hasattr(obj,'__cast__'):
        # If it is typed, we can specify the return type which is what we want
        if getattr(obj.__cast__,'__typed__',False):
            return obj.__cast__(_returns=cls)
        # If not, we'll just have to call it blindly and it can throw its own errors
        else:
            return obj.__cast__()

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
    # This is a bit risky, but we're assuming we're only casting to well-behaving objects (this helps for str/int/etc basic types)
    try:
        return cls(obj)
    except:
        pass

    # We've run out of things to try
    raise NotImplementedError('cannot convert object {obj!r} to {typ!r}'.format(obj=str(obj),typ=str(cls)))

# Use the infix package to allow this to be used in a cool way (if not necessarily a wise one)
@make_infix('sub','rshift')
def to(obj, cls):
    """
    The mirror-image of cast. Cast an object to type

    Infixed for the format '-to>>' making the following equivalent
        `cast(str,5.1) == to(5.1,str) == (5.1 -to>> str) == '5.1'`

    While the `-to>>` format looks cool, be careful as subtraction and bitshift operators
    are in the middle of operator precedence. If using the infix, always use parentheses!

    Args:
        obj: An object to be cast
        cls: Type to cast to

    Returns:
        The object cast to the target class

    Raises:
        TypeError: If the class cannot be converted automatically

    Note:
        This function isn't getting auto-doc'd. I'm assuming it's the infix
    """
    return cast(cls,obj)

# Monkey-patch to get rid of the extra bindings we don't want
def _infix_error(self,other): raise TypeError("unsupported infix format, use '-to>>'")
to.__class__.__rlshift__ = _infix_error
to.__class__.__sub__ = _infix_error
to.rbind.__rlshift__ = _infix_error
to.lbind.__sub__ = _infix_error
