from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_executor import DummyExecutor

class TestIExecutor(AsyncTestCase):

	async def testRunningLogsCorrectly(self):
		"""
		Test that the running method logs the correct state and arguments.

		Returns
		-------
		None
			This test asserts that the log contains the expected RUNNING entry.
		"""
		executor = DummyExecutor()
		executor.running("my_program", "10s")
		self.assertIn(("RUNNING", "my_program", "10s"), executor.logs)

	async def testDoneLogsCorrectly(self):
		"""
		Test that the done method logs the correct state and arguments.

		Returns
		-------
		None
			This test asserts that the log contains the expected DONE entry.
		"""
		executor = DummyExecutor()
		executor.done("my_program", "5s")
		self.assertIn(("DONE", "my_program", "5s"), executor.logs)

	async def testFailLogsCorrectly(self):
		"""
		Test that the fail method logs the correct state and arguments.

		Returns
		-------
		None
			This test asserts that the log contains the expected FAIL entry.
		"""
		executor = DummyExecutor()
		executor.fail("my_program", "2s")
		self.assertIn(("FAIL", "my_program", "2s"), executor.logs)

	async def testNoTimeArgument(self):
		"""
		Test that methods handle the default time argument correctly.

		Returns
		-------
		None
			This test asserts that the log contains entries with an empty time string.
		"""
		executor = DummyExecutor()
		executor.running("prog1")
		executor.done("prog2")
		executor.fail("prog3")
		self.assertIn(("RUNNING", "prog1", ""), executor.logs)
		self.assertIn(("DONE", "prog2", ""), executor.logs)
		self.assertIn(("FAIL", "prog3", ""), executor.logs)

	async def testMultipleLogs(self):
		"""
		Test that multiple calls to methods accumulate logs correctly.

		Returns
		-------
		None
			This test asserts that all log entries are present in the correct order.
		"""
		executor = DummyExecutor()
		executor.running("progA", "1s")
		executor.done("progA", "2s")
		executor.fail("progB", "3s")
		expected = [
			("RUNNING", "progA", "1s"),
			("DONE", "progA", "2s"),
			("FAIL", "progB", "3s")
		]
		self.assertEqual(executor.logs, expected)
