.. MyPyR documentation master file, created by

MyPyR's documentation
======================
A package implementing runtime type-checking and multiple-dispatch method overloading for Python 3+
relying upon `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_ annotation.

This functionality is built around the `TypedObject` class which provides:
    * Automatic or manual (with the `@overload` decorator) overloading of methods
    * The `@inherit` decorator for specifying specific method inheritance (allowing specific overloads to be inherited)
    * A framework for consistent type-casting

In combination, these tools provide a framework for taking advantage of the conveniences
of typed languages when desired while still allowing for the inherent flexibility of Python's duck-typed system.

The system was designed to minimize runtime performance by pre-calculating function
`signatures <https://docs.python.org/3/library/inspect.html#inspect.signature>`_ when first defined and utilizing a custom binding function to identify whether the arguments match the type annotations. This is true multiple-dispatch generic functions as opposed to the builtin `@functools.singledispatch <https://docs.python.org/3/library/functools.html#functools.singledispatch>`_.

Note that the dispatch is greedy, in that it will execute the first function which can be succesfully bound to the arguments. It also considers un-typed arguments to be equivalent to `Any`, making it match any argument.

Examples
--------

The following example walks through some examples of `MyPyR`.








.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. automodule:: mypyr
    :members: