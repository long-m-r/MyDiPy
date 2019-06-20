from mypyr import *

class TestCast(TypedObject,auto_overload=True):
	def __init__(self, obj:str):
		self._val = obj
		self._desc = "I'm a string"

	def __init__(self, obj:int):
		self._val = obj
		self._desc = "I'm an integer"

	def __str__(self):
		return self._desc


print(str(5 -to>> TestCast))
print(str('Test' -to>> TestCast))