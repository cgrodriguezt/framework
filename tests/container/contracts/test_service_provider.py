
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.container.contracts.service_provider import IServiceProvider
from tests.container.contracts.dummy.dummy_service_provider import DummyServiceProvider

class TestIServiceProvider(AsyncTestCase):

	async def testRegisterIsCalled(self):
		"""
		Test that the register method is called and sets the appropriate flag.

		Notes
		-----
		Ensures that the DummyServiceProvider's register method is executed and
		the internal state is updated accordingly.
		"""
		provider = DummyServiceProvider()
		self.assertFalse(provider.register_called)
		await provider.register()
		self.assertTrue(provider.register_called)

	async def testBootIsCalled(self):
		"""
		Test that the boot method is called and sets the appropriate flag.

		Notes
		-----
		Ensures that the DummyServiceProvider's boot method is executed and
		the internal state is updated accordingly.
		"""
		provider = DummyServiceProvider()
		self.assertFalse(provider.boot_called)
		await provider.boot()
		self.assertTrue(provider.boot_called)

	async def testRegisterMustBeImplemented(self):
		"""
		Test that NotImplementedError is raised if register is not implemented.

		Notes
		-----
		Attempts to instantiate a subclass without implementing register should
		raise a TypeError due to the abstract method.
		"""
		class IncompleteProvider(IServiceProvider):
			async def boot(self):
				pass
		try:
			IncompleteProvider()
			self.fail("TypeError was not raised for missing register implementation.")
		except TypeError:
			pass

	async def testBootMustBeImplemented(self):
		"""
		Test that NotImplementedError is raised if boot is not implemented.

		Notes
		-----
		Attempts to instantiate a subclass without implementing boot should
		raise a TypeError due to the abstract method.
		"""
		class IncompleteProvider(IServiceProvider):
			async def register(self):
				pass
		try:
			IncompleteProvider()
			self.fail("TypeError was not raised for missing boot implementation.")
		except TypeError:
			pass
