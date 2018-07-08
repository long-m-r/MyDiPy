import unittest
from mypyr import inherit

class TestInherit(unittest.TestCase):
	def setUp(self):
		class A:
			def test(self): return True
			def test2(self): return True

		class B(A):
			@inherit(A)
			def test(self): return False
			@inherit
			def test2(self): ...

		self.clsa=A()
		self.clsb=B()


	def test_1(self):
		"""Ensure class is inherited"""
		self.assertTrue(self.clsa.test())
		self.assertTrue(self.clsb.test())
		self.assertTrue(self.clsb.test2())
