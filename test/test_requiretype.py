import unittest
from typing import Any
from mydipy import type_check, no_type_check, TypeCheckError

class TestRequireType(unittest.TestCase):
	def setUp(self):
		@type_check
		def fnc(n: int) -> str: return str(n)

		@type_check
		class cls(object):
			def __init__(self,val):
				self.val = val

			def int_test(self,val: int) -> int: return val

			def any_in_test(self,val: Any): return val

			def any_out_test(self, val) -> Any: return val

			def dummy(self, val): pass

			@no_type_check
			def untyped(self, val: int): return val

		self.fnc=fnc
		self.cls=cls
		self.inst=cls(10)

	def test_1(self):
		"""Check whether functions/methods are type checked"""
		self.assertTrue(getattr(self.fnc,'__typed__',False))
		self.assertTrue(getattr(self.inst.__init__,'__typed__',False))
		self.assertTrue(getattr(self.inst.int_test,'__typed__',False))
		self.assertTrue(getattr(self.inst.any_in_test,'__typed__',False))
		self.assertTrue(getattr(self.inst.any_out_test,'__typed__',False))
		self.assertFalse(getattr(self.inst.untyped,'__typed__',False))

	def test_2(self):
		"""Ensure functions behave properly with well-formatted arguments"""
		self.assertEqual(self.fnc(1),str(1))
		self.assertEqual(self.inst.int_test(1),1)
		self.assertEqual(self.inst.int_test(1,_returns=int),1)
		self.assertEqual(self.inst.int_test(1,_returns=Any),1)
		self.assertEqual(self.inst.untyped(3),3)
		self.assertEqual(self.inst.untyped("test"),"test")
		# self.assertEqual(self.inst.any_in_test(1),1)
		# self.assertEqual(self.inst.any_in_test("a",_returns=int),"a")
		# self.assertEqual(self.inst.any_out_test("a",_returns=int),"a")

	def test_3(self):
		"""Ensure functions reject incorrect arguments"""
		with self.assertRaises(TypeError):	self.fnc("a")
		with self.assertRaises(TypeError):	self.inst.int_test("a")
		with self.assertRaises(TypeError):	self.inst.int_test(1,_returns=str)