from abc import ABCMeta, abstractmethod
import typing
from inspect import isfunction, isclass
# Abstract types
class Castable(metaclass=ABCMeta):
    @abstractmethod
    def __cast__(self, cls: typing.Type): ...

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

# class _Union(typing._FinalTypingBase, _root=True):
#     """Union type; Union[X, Y] means either X or Y.

#     To define a union, use e.g. Union[int, str].  Details:

#     - The arguments must be types and there must be at least one.

#     - None as an argument is a special case and is replaced by
#       type(None).

#     - Unions of unions are flattened, e.g.::

#         Union[Union[int, str], float] == Union[int, str, float]

#     - Unions of a single argument vanish, e.g.::

#         Union[int] == int  # The constructor actually returns int

#     - Redundant arguments are skipped, e.g.::

#         Union[int, str, int] == Union[int, str]

#     - When comparing unions, the argument order is ignored, e.g.::

#         Union[int, str] == Union[str, int]

#     - When two arguments have a subclass relationship, the least
#       derived argument is kept, e.g.::

#         class Employee: pass
#         class Manager(Employee): pass
#         Union[int, Employee, Manager] == Union[int, Employee]
#         Union[Manager, int, Employee] == Union[int, Employee]
#         Union[Employee, Manager] == Employee

#     - Similar for object::

#         Union[int, object] == object

#     - You cannot subclass or instantiate a union.

#     - You can use Optional[X] as a shorthand for Union[X, None].
#     """

#     __slots__ = ('__parameters__', '__args__', '__origin__', '__tree_hash__')

#     def __new__(cls, parameters=None, origin=None, *args, _root=False):
#         self = super().__new__(cls, parameters, origin, *args, _root=_root)
#         if origin is None:
#             self.__parameters__ = None
#             self.__args__ = None
#             self.__origin__ = None
#             self.__tree_hash__ = hash(frozenset(('Union',)))
#             return self
#         if not isinstance(parameters, tuple):
#             raise TypeError("Expected parameters=<tuple>")
#         if origin is Union:
#             parameters = typing._remove_dups_flatten(parameters)
#             # It's not a union if there's only one type left.
#             if len(parameters) == 1:
#                 return parameters[0]
#         self.__parameters__ = typing._type_vars(parameters)
#         self.__args__ = parameters
#         self.__origin__ = origin
#         # Pre-calculate the __hash__ on instantiation.
#         # This improves speed for complex substitutions.
#         subs_tree = self._subs_tree()
#         if isinstance(subs_tree, tuple):
#             self.__tree_hash__ = hash(frozenset(subs_tree))
#         else:
#             self.__tree_hash__ = hash(subs_tree)
#         return self

#     def _eval_type(self, globalns, localns):
#         if self.__args__ is None:
#             return self
#         ev_args = tuple(typing._eval_type(t, globalns, localns) for t in self.__args__)
#         ev_origin = typing._eval_type(self.__origin__, globalns, localns)
#         if ev_args == self.__args__ and ev_origin == self.__origin__:
#             # Everything is already evaluated.
#             return self
#         return self.__class__(ev_args, ev_origin, _root=True)

#     def _get_type_vars(self, tvars):
#         if self.__origin__ and self.__parameters__:
#             typing._get_type_vars(self.__parameters__, tvars)

#     def __repr__(self):
#         if self.__origin__ is None:
#             return super().__repr__()
#         tree = self._subs_tree()
#         if not isinstance(tree, tuple):
#             return repr(tree)
#         return tree[0]._tree_repr(tree)

#     def _tree_repr(self, tree):
#         arg_list = []
#         for arg in tree[1:]:
#             if not isinstance(arg, tuple):
#                 arg_list.append(typing._type_repr(arg))
#             else:
#                 arg_list.append(arg[0]._tree_repr(arg))
#         return super().__repr__() + '[%s]' % ', '.join(arg_list)

#     @typing._tp_cache
#     def __getitem__(self, parameters):
#         if parameters == ():
#             raise TypeError("Cannot take a Union of no types.")
#         if not isinstance(parameters, tuple):
#             parameters = (parameters,)
#         if self.__origin__ is None:
#             msg = "Union[arg, ...]: each arg must be a type."
#         else:
#             msg = "Parameters to generic types must be types."
#         parameters = tuple(typing._type_check(p, msg) for p in parameters)
#         if self is not Union:
#             typing._check_generic(self, parameters)
#         return self.__class__(parameters, origin=self, _root=True)

#     def _subs_tree(self, tvars=None, args=None):
#         if self is Union:
#             return Union  # Nothing to substitute
#         tree_args = typing._subs_tree(self, tvars, args)
#         tree_args = typing._remove_dups_flatten(tree_args)
#         if len(tree_args) == 1:
#             return tree_args[0]  # Union of a single type is that type
#         return (Union,) + tree_args

#     def __eq__(self, other):
#         if isinstance(other, _Union):
#             return self.__tree_hash__ == other.__tree_hash__
#         elif self is not Union:
#             return self._subs_tree() == other
#         else:
#             return self is other

#     def __hash__(self):
#         return self.__tree_hash__

#     def __instancecheck__(self, obj):
#         return any(isinstance(obj,c) for c in self.__args__)

#     def __subclasscheck__(self, cls):
#         return any(issubclass(cls,c) for c in self.__args__)
# Union = _Union(_root=True)

# class _Intersection(typing._FinalTypingBase, _root=True):
#     """Intersection type; Intersection[X, Y] means both X and Y.

#     To define a intersection, use e.g. Intersection[int, str].  Details:

#     - The arguments must be types and there must be at least one.

#     - None as an argument is a special case and is replaced by
#       type(None).

#     - Unions of unions are flattened, e.g.::

#         Intersection[Intersection[int, str], float] == Intersection[int, str, float]

#     - Unions of a single argument vanish, e.g.::

#         Intersection[int] == int  # The constructor actually returns int

#     - Redundant arguments are skipped, e.g.::

#         Intersection[int, str, int] == Intersection[int, str]

#     - When comparing unions, the argument order is ignored, e.g.::

#         Intersection[int, str] == Intersection[str, int]

#     - When two arguments have a subclass relationship, the least
#       derived argument is kept, e.g.::

#         class Employee: pass
#         class Manager(Employee): pass
#         Intersection[int, Employee, Manager] == Intersection[int, Employee]
#         Intersection[Manager, int, Employee] == Intersection[int, Employee]
#         Intersection[Employee, Manager] == Employee

#     - Similar for object::

#         Intersection[int, object] == object

#     - You cannot subclass or instantiate a union.

#     - You can use Optional[X] as a shorthand for Intersection[X, None].
#     """

#     __slots__ = ('__parameters__', '__args__', '__origin__', '__tree_hash__')

#     def __new__(cls, parameters=None, origin=None, *args, _root=False):
#         self = super().__new__(cls, parameters, origin, *args, _root=_root)
#         if origin is None:
#             self.__parameters__ = None
#             self.__args__ = None
#             self.__origin__ = None
#             self.__tree_hash__ = hash(frozenset(('Intersection',)))
#             return self
#         if not isinstance(parameters, tuple):
#             raise TypeError("Expected parameters=<tuple>")
#         if origin is Intersection:
#             parameters = typing._remove_dups_flatten(parameters)
#             # It's not a Intersection if there's only one type left.
#             if len(parameters) == 1:
#                 return parameters[0]
#         self.__parameters__ = typing._type_vars(parameters)
#         self.__args__ = parameters
#         self.__origin__ = origin
#         # Pre-calculate the __hash__ on instantiation.
#         # This improves speed for complex substitutions.
#         subs_tree = self._subs_tree()
#         if isinstance(subs_tree, tuple):
#             self.__tree_hash__ = hash(frozenset(subs_tree))
#         else:
#             self.__tree_hash__ = hash(subs_tree)
#         return self

#     def _eval_type(self, globalns, localns):
#         if self.__args__ is None:
#             return self
#         ev_args = tuple(typing._eval_type(t, globalns, localns) for t in self.__args__)
#         ev_origin = typing._eval_type(self.__origin__, globalns, localns)
#         if ev_args == self.__args__ and ev_origin == self.__origin__:
#             # Everything is already evaluated.
#             return self
#         return self.__class__(ev_args, ev_origin, _root=True)

#     def _get_type_vars(self, tvars):
#         if self.__origin__ and self.__parameters__:
#             typing._get_type_vars(self.__parameters__, tvars)

#     def __repr__(self):
#         if self.__origin__ is None:
#             return super().__repr__()
#         tree = self._subs_tree()
#         if not isinstance(tree, tuple):
#             return repr(tree)
#         return tree[0]._tree_repr(tree)

#     def _tree_repr(self, tree):
#         arg_list = []
#         for arg in tree[1:]:
#             if not isinstance(arg, tuple):
#                 arg_list.append(typing._type_repr(arg))
#             else:
#                 arg_list.append(arg[0]._tree_repr(arg))
#         return super().__repr__() + '[%s]' % ', '.join(arg_list)

#     @typing._tp_cache
#     def __getitem__(self, parameters):
#         if parameters == ():
#             raise TypeError("Cannot take a Intersection of no types.")
#         if not isinstance(parameters, tuple):
#             parameters = (parameters,)
#         if self.__origin__ is None:
#             msg = "Intersection[arg, ...]: each arg must be a type."
#         else:
#             msg = "Parameters to generic types must be types."
#         parameters = tuple(typing._type_check(p, msg) for p in parameters)
#         if self is not Intersection:
#             typing._check_generic(self, parameters)
#         return self.__class__(parameters, origin=self, _root=True)

#     def _subs_tree(self, tvars=None, args=None):
#         if self is Intersection:
#             return Intersection  # Nothing to substitute
#         tree_args = typing._subs_tree(self, tvars, args)
#         tree_args = typing._remove_dups_flatten(tree_args)
#         if len(tree_args) == 1:
#             return tree_args[0]  # Intersection of a single type is that type
#         return (Intersection,) + tree_args

#     def __eq__(self, other):
#         if isinstance(other, _Intersection):
#             return self.__tree_hash__ == other.__tree_hash__
#         elif self is not Intersection:
#             return self._subs_tree() == other
#         else:
#             return self is other

#     def __hash__(self):
#         return self.__tree_hash__

#     def __instancecheck__(self, obj):
#         return all(isinstance(obj,c) for c in self.__args__)

#     def __subclasscheck__(self, cls):
#         return all(issubclass(cls,c) for c in self.__args__)

# Intersection = _Intersection(_root=True)