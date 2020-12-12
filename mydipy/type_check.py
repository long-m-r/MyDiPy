from functools import wraps
from itertools import chain
from typing import Any, Type
from collections import defaultdict as ddict

from inspect import Signature, signature, isclass, isfunction, \
    _VAR_KEYWORD,_KEYWORD_ONLY,_VAR_POSITIONAL,_POSITIONAL_ONLY,_POSITIONAL_OR_KEYWORD,_empty

class TypeCheckError(TypeError,NotImplementedError): pass

def type_check(obj):
    """
    A decorator which wraps a function or class to enforce type checking.
    Type checking is matched against typing annotations in Python 3 as defined by
    `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_. No other annotations are
    allowed with `@type_check` (but seriously, does anyone use them for anything else?).

    The decorated function/class must have typing annotations when decorated or it will
    be returned unwrapped.

    When used to decorate a class, all annotated methods will be type checked unless decorated
    with `@no_type_check`.

    Examples:
        An example on applying to a specific function (or class method)

        >>> @type_check
        >>> def typed_function(a: int) -> int:
        ...     return a
        ...
        >>> typed_function(1)
        1
        >>> typed_function("string")
        TypeCheckError: type mismatch for argument 'a'. Got <class 'str'>, needed "<class 'int'>"

    Raises:
        TypeCheckError: If there is a mismatch between a typed parameter and a passed argument when the function is called
        TypeCheckError: If, when the function is called with a named `_returns` argument, that argument is not a subclass of the function's annotated return type. Note that the type of the actual return value is NOT checked.

    Note:
        Functions/methods decorated with `@type_check` accept an optional named argument `_returns`
        which can be used to specify the return type. Note that only the
        annotation of the return value is checked, the return value is not checked
        at runtime (we trust the implementation will return what was promised).
        As such, it is best practice to specify a single and specific return type for a function
        instead of a more general or `Union` type. Use `@overload` to define multiple methods with
        single return types whenever possible.

        Functions/methods used with `@type_check` should not have any parameters named `_returns`.
    """

    # We've already defined this object's typing
    if hasattr(obj,'__typed__'):
        return obj

    # If it's a function
    elif isfunction(obj):
        # If there aren't any annotations, just return
        if not getattr(obj,'__annotations__',{}):
            @wraps(obj)
            def filters(*args,**kwargs):
                kwargs.pop("_returns",None)
                try:
                    return obj(*args,**kwargs)
                except TypeError:
                    raise TypeCheckError ('Invalid types for calling function')
            filters.__typed__=True

            return filters

        # Function will need a signature
        obj.__annotations__['_returns']=Type
        objsig=signature(obj)

        # Create the wrapper function which includes the `_returns` argument
        @wraps(obj)
        def wrapper(*args,**kwargs):
            # See if we're demanding a return type
            returns = kwargs.pop("_returns", Any)
            # Check the arguments to parameters. Raises TypeCheckError if wrong
            _bind_check(objsig, args, kwargs.copy(), returns)

            if getattr(obj,'__typed__',False) or getattr(obj,'__inherit__',False):
                kwargs['_returns']=returns

            # Eval if we make it here
            return obj(*args,**kwargs)
        wrapper.__typed__=True

        # Return the wrapped function
        return wrapper

    elif isclass(obj):
        # Need to iterate through each method in the class
        for k,v in obj.__dict__.items():
            try:
                setattr(obj,k,type_check(v))
            except TypeError:
                pass
        # Mark class as typed and return
        obj.__typed__=True
        return obj
    else:
        raise TypeError('@type_check can only be applied to functions or classes')

def no_type_check(obj):
    """
    A decorator which explicitly marks a class or method to NOT be type checked.

    When used to decorate a class, all annotated methods will not be type checked unless decorated
    with `@type_check`. Note that this is the default behavior, but allows for consistency with
    `@typing.no_type_check <https://docs.python.org/3.6/library/typing.html#typing.no_type_check>`_.

    When used on methods inside a `@type_check` class, `@no_type_check` decorated methods will NOT
    be type checked.

    Note:
        The innermost application of `@type_check` or `@no_type_check` will persist. Therefore, given:

        >>> @type_check
        >>> class c:
        >>>   def f1(self): ...
        >>>
        >>>   @no_type_check
        >>>   def f2(self): ...

        method `f1` will be type checked while method `f2` will not be type checked.
        This behavior means that given:

        >>> @type_check
        >>> @no_type_check
        >>> def f3(self): ...

        `f3` will not be type checked. This is the intended behavior.
    """
    if hasattr(obj,'__typed__'):
        # Already Typed. Ignore
        pass
    elif isfunction(obj):
        # It's a function, we'll mark it below
        pass
    elif isclass(obj):
        # Apply @no_type_check to each class attribute
        for k,v in obj.__dict__.items():
            try:
                setattr(obj,k,no_type_check(v))
            except TypeError:
                pass
    else:
        # It's not a valid type
        raise TypeError('@no_type_check can only be applied to functions or classes')

    # Set __typed__=False if not already set
    setattr(obj,'__typed__',getattr(obj,'__typed__',False))
    return obj


def _bind_check(sig, args, kwargs, return_type = Any) -> None:
    """
    Private method. Don't use directly.
    Modified from inspect.Signature._bind to streamline performance and enforce type checking
    Raises:
       TypeCheckError: If the args/kwargs cannot be successfully mapped to the function signature sig
    """
    #print(sig,args,kwargs,return_type)
    if return_type is Any:
        pass
    elif sig.return_annotation is _empty:
        # Return annotation is unspecified, so this COULD be valid. Try it.
        pass
    elif return_type is None and (sig.return_annotation is not None or None not in sig.return_annotation):
        raise TypeCheckError("function cannot return {ret!r}".format(ret=return_type)) from None
    elif not issubclass(sig.return_annotation,return_type):
        raise TypeCheckError("function cannot return {ret!r}".format(ret=return_type)) from None

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
                        raise TypeCheckError(msg) from None
                    parameters_ex = (param,)
                    break
                elif (param.kind == _VAR_KEYWORD or
                                            param.default is not _empty):
                    # That's fine too - we have a default value for this parameter.  So, lets start parsing `kwargs`, starting with the current parameter
                    parameters_ex = (param,)
                    break
                else:
                    # No default, not VAR_KEYWORD, not VAR_POSITIONAL, not in `kwargs`
                    raise TypeCheckError('missing a required argument: {arg!r}'.format(arg=param.name)) from None

        else:
            # We have a positional argument to process
            try:
                param = next(parameters)
            except StopIteration:
                raise TypeCheckError('too many positional arguments') from None
            else:
                if param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                    # Looks like we have no parameter for this positional argument
                    raise TypeCheckError(
                        'too many positional arguments') from None

                if param.annotation is not _empty and not isinstance(arg_val,param.annotation):
                    # Check the data type, if specified
                    raise TypeCheckError('type mismatch for argument {arg!r}. Got {val!r}, needed {typ!r}'.format(arg=param.name,val=type(arg_val),typ=str(param.annotation))) from None

                if param.kind == _VAR_POSITIONAL:
                    # We have an '*args'-like argument, let's check if we have a datatype
                    if param.annotation is not _empty:
                        # Check each remaining value against the required type
                        for v in arg_vals:
                            if not isinstance(v,param.annotation):
                                # Check the data type if specified
                                raise TypeCheckError('type mismatch for argument {arg!r}. Got {val!r}, needed {typ!r}'.format(arg=param.name,val=type(v),typ=str(param.annotation))) from None
                    break

                if param.name in kwargs:
                    raise TypeCheckError(
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
                raise TypeCheckError('missing a required argument: {arg!r}'.format(arg=param_name)) from None

        else:
            if param.kind == _POSITIONAL_ONLY:
                # This should never happen in case of a properly built Signature object (but let's have this check here to ensure correct behaviour just in case)
                raise TypeCheckError('{arg!r} parameter is positional only, but was passed as a keyword'.format(arg=param.name))

            if param.annotation is not _empty and not isinstance(arg_val,param.annotation):
                # Check the data type if specified
                raise TypeCheckError('type mismatch for argument {arg!r}. Got {val!r}, needed {typ!r}'.format(arg=param.name,val=type(arg_val),typ=str(param.annotation))) from None

    if kwargs:
        if kwargs_param is not None:
            # Process our '**kwargs'-like parameter and check datatypes (if any)
            if kwargs_param.annotation is not _empty:
                for k,v in kwargs.items():
                    if not isinstance(v,kwargs_param.annotation):
                        raise TypeCheckError('type mismatch for argument {arg!r} as **{kwarg!r}. Got {val!r}, needed {typ!r}'.format(arg=k,val=type(v),typ=str(kwargs_param.annotation),kwarg=str(kwargs_param.name))) from None
        else:
            raise TypeCheckError('got an unexpected keyword argument {arg!r}'.format(arg=next(iter(kwargs))))