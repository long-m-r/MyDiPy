from typing import Callable, Type, Any, Mutable, Iterable
from functools import wraps
from inspect import Signature,signature, _VAR_KEYWORD,_KEYWORD_ONLY,_VAR_POSITIONAL,_POSITIONAL_ONLY,_POSITIONAL_OR_KEYWORD,_empty
from itertools import chain

def requiretype(obj):
    return _apply_function_all_methods(_requiretypefunc,'__typed__',obj)

def _requiretypefunc(func: Callable) -> Callable:
    func.__signature__=signature(func)

    @wraps(func)
    def wrapper(*args,**kwargs):
        returns = kwargs.pop("_returns", Any)
        # Raise TypeError if any of our arguments don't match their annotations
        _bind_check(func.__signature__, args, kwargs.copy(),returns) #kwargs will be depleted, so copy is a MUST
        return func(*args,**kwargs)
    return wrapper

def _apply_function_all_methods(aply: Callable, flag: str, obj):
    """helper function to apply a decorator type function to a function or all methods with annotations in a class"""
    # If it's a class
    if isinstance(obj, Type):
        # Loop through methods
        for fname in dir(obj):
            func = getattr(obj, fname)

            # Only type methods which aren't already typed but have annotations

            if not getattr(func,flag,False) and len(getattr(func,'__annotations__',{})) > 0:
                setattr(obj, fname, _apply_function_all_methods(aply,flag,func))

        setattr(obj,flag,True)
        return obj

    # If it's a function
    else:
        if not getattr(obj,flag,False) and len(getattr(obj,'__annotations__',{})) > 0:
            result = aply(obj)
            setattr(result,flag,True)
            return result
        else:
            return obj

# Modification of inspect.Signature._bind method to:
# >> Handle checking with type annotations
# >> Remove return mapping (unnecessary, performance impact)
# >> Raise TypeError if the arguments cannot be mapped to the parameters
def _bind_check(sig: Signature, args: Iterable, kwargs: Mapping, return_type: Type = Any) -> None:
    """Private method. Don't use directly."""
    if return_type is not Any and not issubclass(sig.return_annotation,return_type):
        raise TypeError("function cannot return {ret!r}".format(ret=return_type)) from None

    parameters = iter(sig.parameters.values())
    parameters_ex = ()
    arg_vals = iter(args)

    while True:
        # Let's iterate through the positional arguments and corresponding parameters
        try:
            arg_val = next(arg_vals)
        except StopIteration:
            # No more positional arguments
            try:
                param = next(parameters)
            except StopIteration:
                # No more parameters. That's it. Just need to check that we have no `kwargs` after this while loop
                break
            else:
                if param.kind == _VAR_POSITIONAL:
                    # That's OK, just empty *args.  Let's start parsing kwargs
                    break
                elif param.name in kwargs:
                    if param.kind == _POSITIONAL_ONLY:
                        msg = '{arg!r} parameter is positional only, ' \
                              'but was passed as a keyword'
                        msg = msg.format(arg=param.name)
                        raise TypeError(msg) from None
                    parameters_ex = (param,)
                    break
                elif (param.kind == _VAR_KEYWORD or
                                            param.default is not _empty):
                    # That's fine too - we have a default value for this parameter.  So, lets start parsing `kwargs`, starting with the current parameter
                    parameters_ex = (param,)
                    break
                else:
                    # No default, not VAR_KEYWORD, not VAR_POSITIONAL, not in `kwargs`
                    raise TypeError('missing a required argument: {arg!r}'.format(arg=param.name)) from None

        else:
            # We have a positional argument to process
            try:
                param = next(parameters)
            except StopIteration:
                raise TypeError('too many positional arguments') from None
            else:
                if param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                    # Looks like we have no parameter for this positional argument
                    raise TypeError(
                        'too many positional arguments') from None

                if param.annotation is not _empty and not isinstance(arg_val,param.annotation):
                    # Check the data type, if specified
                    raise TypeError('type mismatch for argument {arg!r}. Got {val!r}, needed {typ!r}'.format(arg=param.name,val=type(arg_val),typ=str(param.annotation))) from None

                if param.kind == _VAR_POSITIONAL:
                    # We have an '*args'-like argument, let's check if we have a datatype
                    if param.annotation is not _empty:
                        # Check each remaining value against the required type
                        for v in arg_vals:
                            if not isinstance(v,param.annotation):
                                # Check the data type if specified
                                raise TypeError('type mismatch for argument {arg!r}. Got {val!r}, needed {typ!r}'.format(arg=param.name,val=type(v),typ=str(param.annotation))) from None
                    break

                if param.name in kwargs:
                    raise TypeError(
                        'multiple values for argument {arg!r}'.format(
                            arg=param.name)) from None

                # arguments[param.name] = arg_val

    # Now, we iterate through the remaining parameters to process
    # keyword arguments
    kwargs_param = None
    for param in chain(parameters_ex, parameters):
        if param.kind == _VAR_KEYWORD:
            # Memorize that we have a '**kwargs'-like parameter
            kwargs_param = param
            continue

        if param.kind == _VAR_POSITIONAL:
            # Named arguments don't refer to '*args'-like parameters.  We only arrive here if the positional arguments ended before reaching the last parameter before *args.
            continue

        param_name = param.name
        try:
            arg_val = kwargs.pop(param_name)
        except KeyError:
            # We have no value for this parameter.  It's fine though, if it has a default value, or it is an '*args'-like parameter, left alone by the processing of positional arguments.
            if (param.kind != _VAR_POSITIONAL and param.default is _empty):
                raise TypeError('missing a required argument: {arg!r}'.format(arg=param_name)) from None

        else:
            if param.kind == _POSITIONAL_ONLY:
                # This should never happen in case of a properly built Signature object (but let's have this check here to ensure correct behaviour just in case)
                raise TypeError('{arg!r} parameter is positional only, but was passed as a keyword'.format(arg=param.name))

            if param.annotation is not _empty and not isinstance(arg_val,param.annotation):
                # Check the data type if specified
                raise TypeError('type mismatch for argument {arg!r}. Got {val!r}, needed {typ!r}'.format(arg=param.name,val=type(arg_val),typ=str(param.annotation))) from None

    if kwargs:
        if kwargs_param is not None:
            # Process our '**kwargs'-like parameter and check datatypes (if any)
            if kwargs_param.annotation is not _empty:
                for k,v in kwargs.items():
                    if not isinstance(v,kwargs_param.annotation):
                        raise TypeError('type mismatch for argument {arg!r} as **{kwarg!r}. Got {val!r}, needed {typ!r}'.format(arg=k,val=type(v),typ=str(kwargs_param.annotation),kwarg=str(kwargs_param.name))) from None
        else:
            raise TypeError('got an unexpected keyword argument {arg!r}'.format(arg=next(iter(kwargs))))