
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_reactor import DummyCommand, DummyReactor

class TestIReactor(AsyncTestCase):

	async def testCommandRegistersAndReturnsICommand(self):
		"""
		Tests that the command method registers a command and returns an ICommand instance.

		Returns
		-------
		None
			This test passes if the returned object simulates ICommand and the command is registered.
		"""
		reactor = DummyReactor()
		dummy = DummyCommand()
		result = reactor.command("foo:bar", dummy)
		self.assertIsNotNone(result)
		self.assertIn("foo:bar", reactor._commands)

	async def testInfoReturnsRegisteredCommands(self):
		"""
		Tests that info returns metadata for all registered commands.

		Returns
		-------
		None
			This test passes if the info list contains the registered command's signature.
		"""
		reactor = DummyReactor()
		reactor.command("foo:bar", DummyCommand())
		info = reactor.info()
		self.assertIsInstance(info, list)
		self.assertEqual(info[0]["signature"], "foo:bar")

	async def testCallExecutesRegisteredCommand(self):
		"""
		Tests that call executes the registered command synchronously and returns its output.

		Returns
		-------
		None
			This test passes if the command's handle method is called and output is correct.
		"""
		reactor = DummyReactor()
		dummy = DummyCommand()
		reactor.command("foo:bar", dummy)
		result = reactor.call("foo:bar", ["arg1"])
		self.assertEqual(result, "handled")
		self.assertTrue(dummy.called)

	async def testCallReturnsNoneForUnknownCommand(self):
		"""
		Tests that call returns None if the command signature is not registered.

		Returns
		-------
		None
			This test passes if the result is None for an unknown command.
		"""
		reactor = DummyReactor()
		result = reactor.call("not:found")
		self.assertIsNone(result)

	async def testCallAsyncExecutesRegisteredCommand(self):
		"""
		Tests that callAsync executes the registered command asynchronously and returns its output.

		Returns
		-------
		None
			This test passes if the command's handle method is called and output is correct.
		"""
		reactor = DummyReactor()
		dummy = DummyCommand()
		reactor.command("foo:bar", dummy)
		result = await reactor.callAsync("foo:bar", ["arg1"])
		self.assertEqual(result, "handled")
		self.assertTrue(dummy.called)

	async def testCallAsyncReturnsNoneForUnknownCommand(self):
		"""
		Tests that callAsync returns None if the command signature is not registered.

		Returns
		-------
		None
			This test passes if the result is None for an unknown command.
		"""
		reactor = DummyReactor()
		result = await reactor.callAsync("not:found")
		self.assertIsNone(result)
