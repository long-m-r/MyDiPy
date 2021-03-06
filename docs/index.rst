MyDiPy's documentation
======================

A package implementing runtime type-checking and multiple-dispatch method overloading for Python 3+
relying upon `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_ annotation.

This functionality is built around the `OverloadObject` class which provides:
    * Automatic or manual (with the `@overload` decorator) overloading of methods
    * The `@inherit` decorator for specifying specific method inheritance (allowing specific overloads to be inherited)
    * A framework for type-casting of objects

In combination, these tools provide a framework for taking advantage of the conveniences
of typed languages when desired while still allowing for the inherent flexibility of Python's duck-typed system.

The system was designed to minimize runtime performance by pre-calculating function
`signatures <https://docs.python.org/3/library/inspect.html#inspect.signature>`_ when first defined and utilizing a custom binding function to identify whether the arguments match the type annotations. This is true multiple-dispatch generic functions as opposed to the builtin `@functools.singledispatch <https://docs.python.org/3/library/functools.html#functools.singledispatch>`_.

Notes:
* Dispatch is greedy, in that it will execute the first function which can be succesfully bound to the arguments. It also considers un-typed arguments to be equivalent to `Any`, making it match any argument.
* This was developed as a proof-of-concept over a couple of weekends for fun. It has been tested on Python 3.6.9 and should generally work for Python 3.

Examples
--------
At a high-level, MyDiPy lets you seamlessly implement type checking, method overloading, inheritance, and multiple dispatch all by inheriting from an instance of `OverloadObject` (or the `TypedMeta` MetaClass).

.. code-block:: python
    :linenos:

    >>>  from mydipy import OverloadObject, overload, inherit
    >>>
    >>> # Create an overloadable parent class
    >>> class A(OverloadObject):
    ...     def test(self, val: int) -> int:
    ...         return -1*val
    ...
    ...     def test(self, val: int) -> str:
    ...         return "VALUE: -"+str(val)
    ...
    >>> # In this class we set `auto_overload=False` so you need the @overload decorator
    >>> class B(OverloadObject, auto_overload=False):
    ...     @overload
    ...     def test(self, val: str) -> str:
    ...         return "B="+val
    ...
    ...     @overload
    ...     def test(self, val: int) -> str:
    ...         return "B="+str(int)
    ...
    ...     @overload
    ...     def test(self, val):
    ...         raise ValueError()
    ...
    >>> # Now let's inherit from A and B and see what happens
    >>> class C(A,B,auto_overload=True):
    ...
    ...     def test(self, val: int) -> int:
    ...         return -val*5
    ...
    ...     # Here we want to go to Class A for any calls where val is an int and we want a str returned
    ...     @inherit(A)
    ...     def test(self, val: int) -> str: ...
    ...
    ...     # Similarly we want to go to Class B for anything where val is a str
    ...     @inherit(B)
    ...     def test(self, val: str): ...
    ...
    >>> ex = C()
    >>> print(ex.test(1))
    -5
    >>> print(ex.test(1,_returns=str))
    VALUE: -1
    >>> print(ex.test('test'))
    B=test

Furthermore, there is a basic casting system built into MyDiPy (this is in the early stages):

.. code-block:: python
    :linenos:

    >>> from mydipy import OverloadObject, cast, to, inherit
    >>> 
    >>> class Currency(OverloadObject):
    ...     """Generic parent Currency Class"""
    ...     exchange_ratio = 0.0
    ...     prefix = ''
    ... 
    ...     def __init__(self, value : float):
    ...         # Value of our currency
    ...         self.value = value
    ... 
    ...     def __str__(self):
    ...         # Pretty form
    ...         return self.prefix + str(self.value)
    ... 
    >>> class Dollar(Currency):
    ...     """Dollar currency. Use this as the basis for all exchanges"""
    ...     exchange_ratio = 1.0
    ...     prefix = '$'
    ... 
    ...     # Let's convert this currency back into dollars so we can do exchanges
    ...     def __cast__(self) -> Currency:
    ...         return Dollar(self.value * self.exchange_ratio)
    ...     # This will mean we will automatically use __str__, __int__, and __nonzero__ to convert to str, int, and bool respectively
    ...     @inherit
    ...     def __cast__(self): ...
    ... 
    ...     def __add__(self, oth : Currency) -> Currency:
    ...         # Convert both to Dollars to do addition
    ...         if type(oth) != Dollar:
    ...             oth = cast(Dollar,oth)
    ...         if type(self) != Dollar:
    ...             me = cast(Dollar,self)
    ...         else:
    ...             me = self
    ...         return Dollar(me.value * oth.value)
    ... 
    >>> class Euro(Dollar):
    ...     exchange_ratio = 1.21
    ...     prefix = '€'
    ... 
    >>> # Define some amount of dollars and euros
    >>> a = Dollar(5)
    >>> b = Euro(3)
    >>> # The next two are equivalent!
    >>> print(cast(Dollar,b))
    $3.63
    >>> print(b -to>> Dollar)
    $3.63
    >>> # Automatically unit convert for addition
    >>> print(a+b)
    $18.15

To enable casting, simply define `__cast__(self) -> <Output Type>` magic methods to your classes.
Optionally, you may want to `@inherit(OverloadObject)` for `__cast__(self)` at the end in order to
get automatic casting to str, int, and bool via the normal Python magic methods.


Known Issues/Feature Requests
-----------------------------
* Proper handling of arrays and types
* Proper handling of \*args and \*\*kwargs
* Automatic type casting of objects in method parameters when no other definition matches


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. automodule:: mydipy
    :members: