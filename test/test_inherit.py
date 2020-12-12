import unittest
from mydipy import inherit

class TestInherit(unittest.TestCase):
	def setUp(self):
		class A:
			def test(self): return 1
			def test2(self): return 2

		class B(A):
			# This function body will be ignored since it is inherited
			@inherit(A)
			def test(self): return 0

			# This is the preffered method for writing an inherited function
			@inherit
			def test2(self): ...

		self.clsa=A()
		self.clsb=B()


	def test_1(self):
		"""Ensure class is inherited, all should be true"""
		self.assertEqual(self.clsa.test(),1)
		self.assertEqual(self.clsb.test(),1)
		self.assertEqual(self.clsb.test2(),2)
