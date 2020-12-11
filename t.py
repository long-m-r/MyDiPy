
from mypyr import overload, TypedObject, inherit, TypedMeta

class A(TypedObject):
    def __init__(self):
        self.str="A"
    @overload
    def test(self, val: str) -> str: return "A="+self.str
    @overload
    def test(self, val: bool) -> float: return 1.1
    @overload
    def test(self,val): raise ValueError()

class B(TypedObject):
    def __init__(self):
        self.str="B"

    @overload
    def test(self, nam: str) -> str: return "B="+self.str
    @overload
    def test(self, nam: int): return "B="+str(int)
    @overload
    def test(self, nam): raise ValueError()

class C(TypedObject,auto_overload=True):
    def __init__(self):
        self.str="C"

    def test(self, res: str, mul: int=3) -> str:
        return "C="+self.str+":"+res*mul
    def test(self, nam: int):
        return "C="+str(nam)
    def test(self, *args, **kwargs):
        raise AttributeError()


class D(A,B,C,metaclass=TypedMeta,auto_overload=True):
    def __init__(self):
        self.str="D"

    def test(self, val: int) -> int: return -val
    def test(self, val: int) -> str: return ("("+str(val)+")" if val>0 else str(val))
    def test(self, val: float) -> str: return ("yes" if val<0 else "no")
    def test(self, val: float) -> int: return -int(val)
    def test(self, *args: int) -> int: return -sum(args)
    @inherit(A)
    def test(self, val: str) -> str: ...
    @inherit(B)
    def test(self, nam: str): ...
    @inherit(C)
    def test(self, *args, **kwargs): ...

test=D()

print(test.test(nam='a'))

#print(test.test.__annotations__)

#print(test._overloads)
#bt = B()
#print(bt.test(nam='1'))