from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.contracts.base_command import IBaseCommand
from tests.console.contracts.dummy.dummy_command import DummyCommand

class TestIBaseCommand(AsyncTestCase):
	"""
	Unit tests for the IBaseCommand abstract base class and its contract.
	"""

	async def testSignatureAndDescription(self):
		"""
		Test that the DummyCommand has correct signature and description attributes.

		Returns
		-------
		None
		"""
		cmd = DummyCommand()
		assert cmd.signature == "dummy"
		assert cmd.description == "A dummy command for testing."

	async def testTimestampsDefault(self):
		"""
		Test that timestamps attribute is True by default.

		Returns
		-------
		None
		"""
		cmd = DummyCommand()
		assert cmd.timestamps is True

	async def testArgumentsStorage(self):
		"""
		Test that arguments and _args are correctly set and accessible.

		Returns
		-------
		None
		"""
		cmd = DummyCommand()
		assert isinstance(cmd.arguments, list)
		assert cmd._args["foo"] == "bar"

	async def testHandleExecution(self):
		"""
		Test that handle() executes and sets executed flag.

		Returns
		-------
		None
		"""
		cmd = DummyCommand()
		assert not cmd.executed
		cmd.handle()
		assert cmd.executed

	async def testAbstractHandleRaises(self):
		"""
		Test that calling handle() on IBaseCommand raises NotImplementedError.

		Returns
		-------
		None
		"""
		class IncompleteCommand(IBaseCommand):
			signature = "incomplete"
			description = "Should not implement handle."
		try:
			IncompleteCommand()
			assert False, "TypeError not raised"
		except TypeError:
			pass
