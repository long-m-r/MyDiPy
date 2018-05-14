from mypyr import *

class test(CastableObject):
    def __cast__(self, cls) -> int: return "Integer"
    def __cast__(self, cls) -> bool: return "Boolean"

    @inherit
    def __cast__(self, cls): ...

    def __str__(self):
        return "String"

a=test()
# print(a.__cast__)

print(cast(int,a))
print(cast(bool,a))
print(cast(str,a))
print(cast(float,a))

# class a1(metaclass=OMeta):
#     @type_check
#     def test(self, cls: int): return "Class A1"

# class a2(metaclass=OMeta):
#     @type_check
#     def test(self, cls: str): return "Class A2"


# class b(a1,a2):
#     @inherit
#     def test(self, cls): return "Class B"

# temp=b()
# print(temp.test(1))