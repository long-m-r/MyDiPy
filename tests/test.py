#!/usr/bin/env python3
import sys
sys.path.insert(0,'../src')

from typing import Type

from inherit import *
from overload import *
from cast import *

class A(castable):
	def __init__(self):
		self.val=1
		self.str="A"

class B(A):
	def __init__(self):
		self.val=2
		self.str="B"

	@overload
	def __cast__(self, cls: Type) -> int:
		return self.val

	@overload
	@inherit(A)
	def __cast__(self, cls: Type): ...

refresh()

b=B()
print(cast(int,b))
print(cast(str,b))


a=A()
print(cast(str,a))
print(cast(int,a))