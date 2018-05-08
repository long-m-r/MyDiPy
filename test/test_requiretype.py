import unittest
from typing import Any
from mypyr import requiretype

class TestRequireType(unittest.TestCase):
	def setUp(self):
		@requiretype
		def fnc(n: int) -> str: return str(n)

		@requiretype
		class cls(object):
			def __init__(self,val):
				self.val = val

			def int_test(self,val: int) -> int: return val
			def str_test(self,val: str) -> str: return val
			def any_in_test(self,val: Any): return val
			def any_out_test(self, val) -> Any: return val
			def dummy(self, val): pass

		self.fnc=fnc
		self.cls=cls
		self.inst=cls(10)


	def test_1(self):
		"""Check whether functions/methods are type checked"""
		self.assertTrue(getattr(self.fnc,'__typed__',False))
		self.assertFalse(getattr(self.inst.__init__,'__typed__',False))
		self.assertTrue(getattr(self.inst.int_test,'__typed__',False))
		self.assertTrue(getattr(self.inst.str_test,'__typed__',False))
		self.assertTrue(getattr(self.inst.any_in_test,'__typed__',False))
		self.assertTrue(getattr(self.inst.any_out_test,'__typed__',False))
		self.assertFalse(getattr(self.inst.dummy,'__typed__',False))

	def test_2(self):
		"""Ensure functions behave properly with well-formatted arguments"""
		self.assertEqual(self.fnc(1),str(1))
		self.assertEqual(self.inst.int_test(1),1)
		self.assertEqual(self.inst.int_test(1,_returns=int),1)
		self.assertEqual(self.inst.int_test(1,_returns=Any),1)
		self.assertEqual(self.inst.str_test("a"),"a")
		self.assertEqual(self.inst.str_test("a",_returns=str),"a")
		self.assertEqual(self.inst.str_test("a",_returns=Any),"a")
		# self.assertEqual(self.inst.any_in_test(1),1)
		# self.assertEqual(self.inst.any_in_test("a",_returns=int),"a")
		# self.assertEqual(self.inst.any_out_test("a",_returns=int),"a")

	def test_3(self):
		"""Ensure functions reject incorrect arguments"""
		with self.assertRaises(TypeError):	self.fnc("a")
		with self.assertRaises(TypeError):	self.inst.int_test("a")
		with self.assertRaises(TypeError):	self.inst.int_test(1,_returns=str)
		with self.assertRaises(TypeError):	self.inst.str_test(1)
		with self.assertRaises(TypeError):	self.inst.str_test("a",_returns=int)