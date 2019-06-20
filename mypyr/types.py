# raise NotImplementedError('mypyr.types not yet impelemented')

from abc import ABCMeta, abstractmethod
import typing
from inspect import isfunction, isclass
# Abstract types
class Castable(metaclass=ABCMeta):
    @abstractmethod
    def __cast__(self): ...

class _FunctionMeta(ABCMeta):
    def __instancecheck__(self,obj):
        return isfunction(obj)
    def __subclasscheck__(self,cls):
        return False
class Function(metaclass=_FunctionMeta):
    pass

class _ClassMeta(ABCMeta):
    def __instancecheck__(self,obj):
        return isclass(obj)
    def __subclasscheck__(self,cls):
        return False
class Class(metaclass=_ClassMeta):
    pass


class _UnionMeta(ABCMeta):
    def __instancecheck__(self,obj):
        return any(isinstance(a,obj) for a in self.__args__)

    def __subclasscheck__(self,cls):
        return any(issubclass(a,cls) for a in self.__args__)
