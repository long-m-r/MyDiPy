#!/usr/bin/env python3

import sys
sys.path.insert(0,'../src')

from decorators import exceptinherit

class A:

	def typee(self,val):
		# return("Got "+str(val)+" in typee")
		raise ValueError("Super Oops")

	def attre(self,val):
		return("Got "+str(val)+" in attre")

	def othere(self,val):
		return("Got "+str(val)+" in othere")

	def solo(self):
		pass

class B(A):

	@exceptinherit((TypeError))
	def typee(self,val):
		raise TypeError("Oops")

	@exceptinherit((AttributeError,ValueError))
	def attre(self,val):
		if val==1:
			raise AttributeError("Oops")
		elif val==2:
			raise ValueError("Oops")
		raise TypeError("Oops")

	@exceptinherit((AttributeError))
	def othere(self,val):
		raise ValueError("Oops")

a=A()
b=B()

# print(inspect.signature(B.typee))
print(b.attre(1))
print(b.attre(2))
print(b.typee("test"))