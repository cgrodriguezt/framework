
from orionis.console.contracts.kernel import IKernelCLI
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_kernel_cli import DummyKernelCLI

class TestIKernelCLI(AsyncTestCase):

	async def testHandleStoresArguments(self):
		"""
		Test that the handle method stores the provided arguments.

		Parameters
		----------
		self : TestIKernelCLI
			The test case instance.

		Returns
		-------
		None
		"""
		dummy = DummyKernelCLI()
		args = ["run", "--option", "value"]
		dummy.handle(args)
		self.assertEqual(dummy.handled_args, args)

	async def testHandleWithEmptyArguments(self):
		"""
		Test that the handle method works with an empty argument list.

		Parameters
		----------
		self : TestIKernelCLI
			The test case instance.

		Returns
		-------
		None
		"""
		dummy = DummyKernelCLI()
		args = []
		dummy.handle(args)
		self.assertEqual(dummy.handled_args, args)

	async def testIKernelCLIAbstractMethod(self):
		"""
		Test that calling handle on IKernelCLI directly raises NotImplementedError.

		Parameters
		----------
		self : TestIKernelCLI
			The test case instance.

		Returns
		-------
		None
		"""
		class NoImplKernelCLI(IKernelCLI):
			def handle(self, args: list) -> None:
				super().handle(args)
		cli = NoImplKernelCLI()
		try:
			cli.handle(["test"])
		except NotImplementedError:
			pass
		else:
			self.fail("NotImplementedError was not raised.")
