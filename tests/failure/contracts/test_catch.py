
from orionis.failure.contracts.catch import ICatch
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.failure.contracts.dummy.dummy_catch import DummyCatch

class TestICatch(AsyncTestCase):

	async def testExceptionIsCalled(self):
		"""
		Test that the exception method is called and stores arguments.

		Returns
		-------
		None
			This test does not return any value. It asserts side effects.
		"""
		dummy = DummyCatch()
		kernel = object()
		request = object()
		exc = Exception("Test error")
		dummy.exception(kernel, request, exc)
		self.assertTrue(dummy.called)
		self.assertEqual(dummy.last_args, (kernel, request, exc))

	async def testExceptionWithNoneKernel(self):
		"""
		Test that exception method handles None as kernel argument.

		Returns
		-------
		None
			This test does not return any value. It asserts side effects.
		"""
		dummy = DummyCatch()
		request = object()
		exc = Exception("Test error")
		dummy.exception(None, request, exc)
		self.assertTrue(dummy.called)
		self.assertEqual(dummy.last_args, (None, request, exc))

	async def testExceptionWithDifferentExceptionTypes(self):
		"""
		Test that exception method can handle different exception types.

		Returns
		-------
		None
			This test does not return any value. It asserts side effects.
		"""
		dummy = DummyCatch()
		kernel = object()
		request = object()
		for exc in [ValueError("value error"), RuntimeError("runtime error"), KeyboardInterrupt()]:
			dummy.called = False
			dummy.last_args = None
			dummy.exception(kernel, request, exc)
			self.assertTrue(dummy.called)
			self.assertEqual(dummy.last_args, (kernel, request, exc))

	async def testICatchIsAbstract(self):
		"""
		Test that ICatch cannot be instantiated directly due to abstract methods.

		Returns
		-------
		None
			This test does not return any value. It asserts that TypeError is raised.
		"""
		try:
			ICatch()
		except TypeError:
			pass
		else:
			self.fail("ICatch should not be instantiable directly.")
