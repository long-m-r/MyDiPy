.. MyPyR documentation master file, created by

MyPyR's documentation
======================
A package implementing runtime type-checking and method overloading for Python 3+
relying upon `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_ annotation.

It provides:
    * A `@requiretype` decorator to enforce type-checking of a function at runtime
    * An `@overload` decorator allowing overloading of functions
    * A `@inherit` decorator for specifying specific method inheritance
    * A framework for consistent type-casting


In combination, these tools provide a framework for taking advantage of the best
features of typed languages when desired while still allowing for the inherent
flexibility of Python's duck-typed system.

The system was designed to minimize runtime impact by performing as much computation
when the decorated functions are first defined. Calling decorated functions
will necessarily impose some burden; however, this module is designed to minimize
this impact.

Examples
--------

The following example walks through many of the highlights of `MyPyR`.

If we define a simple wrapper class:






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