>>> from mypyr import OverloadObject, cast, to, inherit
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
>>> 
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
>>> 
>>> class Euro(Dollar):
...     exchange_ratio = 1.21
...     prefix = '€'
>>> 
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
