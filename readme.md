# MyDiPy

What if Python was a typed language? Well that probably break a lot of existing code. But what if it could act like a typed when you want it to but retain the utility of a duck typed language otherwise?

[PEP 484](https://www.python.org/dev/peps/pep-0484/) introduced nice annotations for Python 3.5+ that could be used as type hints, and packages such as [MyPy](https://github.com/python/mypy) allow you to leverage these to detect errors prior to runtime.

What MyDiPy does is extend this functionality so that it *actually works at runtime* in a way you would expect. That means overloading functions, type checking on arguments, multiple dispatch, inheriting from parent classes, and even a unified casting framework.

## Note
This is a proof-of-concept project from a couple of weekends of tinkering. I have not used this in any other projects (yet). While it seems to work remarkably well, there are [known issues](https://github.com/long-m-r/MyDiPy/issues) that need resolving.

## Examples
The first example highlights method overloading, multiple dispatch, and overloading:
``` python
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
...         return "B="+self.str
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
```

And here's an example that shows how casting can work in practice:
``` python
>>> from MyDiPy import OverloadObject, cast, to, inherit
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
```

Seem interesting to you? Read on for more details.

## Details
See [the module documentation](https://htmlpreview.github.io/?https://github.com/long-m-r/MyDiPy/blob/main/html/index.html) for details and examples.

At a high level, MyDiPy includes:
- `OverloadObject` Class: This is what the rest of the module is built around. Any class which inherits from this may define method multiple times and watch the correct version be called
    - `@overload` Decorator: Used to specify which methods to overload when `auto_overload=False` in `OverloadObject` child classes
    - `@inherit` Decorator: Allows you to inherit method overloads from specific classes. Really only useful in `OverloadObject` classes
- `@type_check` Decorator: Used to enforce type checking based on function annotations before execution. Automatically applied to overload functions
    - `@no_type_check` Decorator: Explicitly flag a function as not being type checked
    - `TypeCheckError` Error: Thrown whenever a type check fails on function/method invocation
- `cast` and `to` Functions: Cast an `OverloadObject`-based class with `__cast__(self) -> <Class>` methods defined to the target class.
    - `cast` is identical in principle to MyPy's function
    - `to` is the reverse version that also has an infix for `-to>>` meaning `cast(str, a) == to(a, str) == (a -to>> str)`
- `@OverloadFunction` Decorator: This is a decorator/class for overloading functions outside of class methods
- `TypedMeta` MetaClass: This is a MetaClass which allows overloading, but does not have methods built in for casting. Supports the `auto_overload` option. Generally recommend using `OverloadObject` Class unless you have a specific reason not to.

