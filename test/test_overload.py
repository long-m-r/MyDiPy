import unittest
from mypyr import overload, TypedObject, inherit

class TestOverload(unittest.TestCase):
	def setUp(self):
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


		class D(A,B,C):
			def __init__(self):
				self.str="D"

			@overload
			def test(self, val: int) -> int: return -val
			@overload
			def test(self, val: int) -> str: return ("("+str(val)+")" if val>0 else str(val))
			@overload
			def test(self, val: float) -> str: return ("yes" if val<0 else "no")
			@overload
			def test(self, val: float) -> int: return -int(val)
			@overload
			def test(self, *args: int) -> int: return -sum(args)
			@overload
			@inherit(A)
			def test(self, val: str) -> str: ...
			@overload
			@inherit(B)
			def test(self, nam: str): ...
			@overload
			@inherit(C)
			def test(self,*args, **kwargs): ...

		print(B.test.__typed__)
		self.cls=D()


	def test_1(self):
		"""Ensure correct functions are called"""
		self.assertEqual(self.cls.test(1),-1)
		self.assertEqual(self.cls.test(val=1),-1)
		self.assertEqual(self.cls.test(1,_returns=int),-1)
		self.assertEqual(self.cls.test(1,_returns=str),"(1)")
		self.assertEqual(self.cls.test(val=1,_returns=str),"(1)")
		self.assertEqual(self.cls.test(-0.1),"yes")
		self.assertEqual(self.cls.test(-0.1,_returns=str),"yes")
		self.assertEqual(self.cls.test(20.9,_returns=int),-20)
		self.assertEqual(self.cls.test(1,2,3,4),-10)
		self.assertEqual(self.cls.test(1,2,3,4,_returns=int),-10)
		self.assertEqual(self.cls.test("super"),"A=D")
		self.assertEqual(self.cls.test(val="super"),"A=D")
		self.assertEqual(self.cls.test(nam="super"),"B=D")
		self.assertEqual(self.cls.test(nam=2),"C=2")
		self.assertEqual(self.cls.test("super",2),"C=D:supersuper")

	def test_2(self):
		"""Check annotations of overloaded objects"""
		a = self.cls.test.__annotations__
		self.assertSetEqual(set(a['val']),set([int,float,str]))
		self.assertSetEqual(set(a['nam']),set([str]))
		self.assertSetEqual(set(a['return']),set([str,int]))

	def test_3(self):
		"""Error out"""
		with self.assertRaises(AttributeError):	self.cls.test([])
		with self.assertRaises(AttributeError):	self.cls.test(1,2,3,"h")
		with self.assertRaises(AttributeError): self.cls.test(val="a",_returns=float)
		with self.assertRaises(ValueError): self.cls.test(nam="a",_returns=float)