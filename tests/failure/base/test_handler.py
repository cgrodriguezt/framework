from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.failure.base.handler import BaseExceptionHandler
from tests.failure.base.dummy.dummy_console import DummyConsole
from tests.failure.base.dummy.dummy_logger import DummyLogger
from tests.failure.base.dummy.dummy_request import DummyRequest

class TestBaseExceptionHandler(AsyncTestCase):
	"""
	Unit tests for BaseExceptionHandler class.
	"""

	async def testDestructureException(self):
		"""
		Test that destructureException returns a Throwable with correct attributes.

		Returns
		-------
		None
		"""
		handler = BaseExceptionHandler()
		exc = ValueError("Test error", 123)
		throwable = await handler.destructureException(exc)
		self.assertEqual(throwable.classtype, ValueError)
		self.assertEqual(throwable.message, "Test error")
		self.assertEqual(throwable.args, ("Test error", 123))
		self.assertIsNotNone(throwable.traceback)

	async def testShouldIgnoreExceptionFalse(self):
		"""
		Test shouldIgnoreException returns False for exceptions not in dont_catch.

		Returns
		-------
		None
		"""
		handler = BaseExceptionHandler()
		exc = RuntimeError("Should not ignore")
		result = await handler.shouldIgnoreException(exc)
		self.assertFalse(result)

	async def testShouldIgnoreExceptionTrue(self):
		"""
		Test shouldIgnoreException returns True for exceptions in dont_catch.

		Returns
		-------
		None
		"""
		class CustomException(Exception):
			pass
		handler = BaseExceptionHandler()
		handler.dont_catch = [CustomException]
		exc = CustomException("Ignore me")
		result = await handler.shouldIgnoreException(exc)
		self.assertTrue(result)

	async def testReportLogsError(self):
		"""
		Test that report logs the error message using the provided logger.

		Returns
		-------
		None
		"""
		handler = BaseExceptionHandler()
		logger = DummyLogger()
		exc = KeyError("Log this error")
		throwable = await handler.report(exc, logger)
		self.assertIn("[KeyError] Log this error", logger.logs[0])
		self.assertEqual(throwable.classtype, KeyError)

	async def testRenderCLIOutputsException(self):
		"""
		Test that renderCLI logs and outputs the exception to the console.

		Returns
		-------
		None
		"""
		handler = BaseExceptionHandler()
		logger = DummyLogger()
		request = DummyRequest()
		console = DummyConsole()
		exc = Exception("CLI error")
		await handler.renderCLI(exc, request, logger, console)
		self.assertIn("CLI Error: CLI error (Args: {'foo': 'bar'})", logger.logs[0])
		self.assertIn("Exception: CLI error", "".join(console.output))

	async def testShouldIgnoreExceptionTypeError(self):
		"""
		Test shouldIgnoreException raises TypeError if argument is not an exception.

		Returns
		-------
		None
		"""
		handler = BaseExceptionHandler()
		with self.assertRaises(TypeError):
			await handler.shouldIgnoreException("not an exception")

	async def testReportTypeError(self):
		"""
		Test report raises TypeError if argument is not an exception.

		Returns
		-------
		None
		"""
		handler = BaseExceptionHandler()
		logger = DummyLogger()
		with self.assertRaises(TypeError):
			await handler.report("not an exception", logger)

	async def testRenderCLITypeError(self):
		"""
		Test renderCLI raises TypeError if arguments are of wrong type.

		Returns
		-------
		None
		"""
		handler = BaseExceptionHandler()
		logger = DummyLogger()
		request = DummyRequest()
		console = DummyConsole()
		with self.assertRaises(TypeError):
			await handler.renderCLI("not an exception", request, logger, console)
		with self.assertRaises(TypeError):
			await handler.renderCLI(Exception("ok"), "not a request", logger, console)
