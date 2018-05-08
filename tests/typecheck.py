#!/usr/bin/env python3
import sys
sys.path.insert(0,'../src')
from decorators import typecheck

@typecheck
def test(msg:str):
	print(msg)


class A:

	@typecheck
	def test(self,a:int,b:str="hello "):
		return a*b

	@typecheck
	def test2(self,a:int,b:str="hello ") -> str:
		return a*b

	@typecheck
	def test3(self,*args:int,**kwargs:str) -> list:
		return [a for a in args],kwargs

# test(msg="This one should work.")
# test(msg=-1)

a=A()
# print(a.test(a=1,b="whatever"))

print(a.test2(a=1,b="required",_returns=str))
print(a.test2.__annotations__)

print(a.test3(1,2,20,a="hello",_returns=list))