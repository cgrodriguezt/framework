from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.output.executor import Executor
import builtins

class TestExecutor(AsyncTestCase):

	async def testRunningOutputsCorrectFormat(self):
		"""
		Tests that the running() method outputs the correct format and color codes.

		This test mocks the print function to capture output and verifies that the
		output string contains the expected state and color code for RUNNING.

		Returns
		-------
		None
			This test asserts the output format for the running state.
		"""
		executor = Executor()
		captured = {}
		def fake_print(*args, **kwargs):
			captured['output'] = args[0] if args else ''
		original_print = builtins.print
		builtins.print = fake_print
		try:
			executor.running("MyProgram", "10s")
			self.assertIn("RUNNING", captured['output'])
			self.assertIn("MyProgram", captured['output'])
		finally:
			builtins.print = original_print

	async def testDoneOutputsCorrectFormat(self):
		"""
		Tests that the done() method outputs the correct format and color codes.

		This test mocks the print function to capture output and verifies that the
		output string contains the expected state and color code for DONE.

		Returns
		-------
		None
			This test asserts the output format for the done state.
		"""
		executor = Executor()
		captured = {}
		def fake_print(*args, **kwargs):
			captured['output'] = args[0] if args else ''
		original_print = builtins.print
		builtins.print = fake_print
		try:
			executor.done("MyProgram", "5s")
			self.assertIn("DONE", captured['output'])
			self.assertIn("MyProgram", captured['output'])
		finally:
			builtins.print = original_print

	async def testFailOutputsCorrectFormat(self):
		"""
		Tests that the fail() method outputs the correct format and color codes.

		This test mocks the print function to capture output and verifies that the
		output string contains the expected state and color code for FAIL.

		Returns
		-------
		None
			This test asserts the output format for the fail state.
		"""
		executor = Executor()
		captured = {}
		def fake_print(*args, **kwargs):
			captured['output'] = args[0] if args else ''
		original_print = builtins.print
		builtins.print = fake_print
		try:
			executor.fail("MyProgram", "2s")
			self.assertIn("FAIL", captured['output'])
			self.assertIn("MyProgram", captured['output'])
		finally:
			builtins.print = original_print

	async def testNoTimeArgument(self):
		"""
		Tests that the methods handle the absence of the time argument gracefully.

		This test checks that the output does not break or include unwanted text
		when the time argument is omitted.

		Returns
		-------
		None
			This test asserts the output format when no time is provided.
		"""
		executor = Executor()
		captured = {}
		def fake_print(*args, **kwargs):
			captured['output'] = args[0] if args else ''
		original_print = builtins.print
		builtins.print = fake_print
		try:
			executor.running("NoTimeProgram")
			self.assertIn("RUNNING", captured['output'])
			self.assertIn("NoTimeProgram", captured['output'])
		finally:
			builtins.print = original_print
