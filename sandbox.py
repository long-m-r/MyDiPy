from mypyr import *
from typing import Type
from functools import wraps

def _merge_annotations(curr,new):
	"""Private function. Don't use directly."""
	# Merge annotations by items in new
	for k,v in new.__annotations__.items():
		# Get a set of the annotations
		nv = set(v) if isinstance(v,Iterable) else set([v])

		ov = curr.__annotations__.get(k,[])

		# Merge existing annotations with new ones
		nv |= set(ov) if isinstance(ov,Iterable) else set([ov])

		# Apply
		curr.__annotations__[k] = tuple(nv)

	# Merge docstrings as well, if there are any
	if new.__doc__ is not None:
		if curr.__doc__ is None:
			curr.__doc__ = new.__doc__
		else:
			curr.__doc__ += "\n\n"+new.__doc__

class wrapper:
	__overload__=True

	def __init__(self,func):
		self._functions=[type_check(func)]

		# Wrap the class with the function
		wraps(func)(self)


	def __call__(_self,*args,**kwargs):
		for f in _self._functions:
			try:
				return f(*args,**kwargs)
			except TypeCheckError:
				pass
		raise NotImplementedError("could not find valid @overload function for '"+_self.__qualname__+"'")

	# Allow defining output
	def __gt__(self,other):
		print(other)
		return self

	def overload(self,func):
		self._functions.append(type_check(func))
		_merge_annotations(self,func)

@wrapper
def t(a:int) -> int:
	return -a

(t>int)(4)

class test:
	def __init__(self):
		self.p='test'

	@wrapper
	def t(self,b):
		print(self.p,b)



b=test()

b.t(' text')