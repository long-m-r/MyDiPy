#!/usr/bin/env python3
import sys
sys.path.insert(0,'../src')

from inherit import *
from typed import typed

class A:

	@typed
	def typee(self,val:str):
		return("Got "+str(val)+" in A.typee")

	# @typecheck
	def attre(self,val:str="") -> int:
		return("Got "+str(val)+" in A.attre")

	def othere(self,val):
		return("Got "+str(val)+" in A.othere")


class B(A):
	# # @overload
	# def attre(self,val:str) -> str:
	# 	return("Got "+val+" in B.attre one")
	# # @overload
	# def attre(self,num:int) -> str:
	# 	return("Got "+str(num)+" in B.attre two")

	# @overload
	@inherit(A)
	def attre(self,*args,**kwargs) -> str: ...

# refresh()

# a=A()
# b=B()

# print(b.attre(val="wonder of wonders ",_returns=str))
