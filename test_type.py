from mypyr import *

class A(TypedObject):
    intval:int = 30
    strval:str
    boolval:bool
    floatval:float
    def test(self,a:float):
        return 'float '+str(a)
    def test(self,a:str):
        return 'str '+a

class B(A):
    def test(self,a:int):
        return 'int '+str(a)
    @inherit
    def test(self,a):
        ...
    def test(self,a:str):
        return 'strB '+a
    def __cast__(self, cls) -> str:
        return "string"

a=A()
b=B()
b.test(1.)