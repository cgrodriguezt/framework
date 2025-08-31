
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.failure.base.handler import BaseExceptionHandler
from orionis.services.log.contracts.log_service import ILogger
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.console import IConsole
import types

class DummyLogger(ILogger):
	def __init__(self):
		self.logs = []
	def debug(self, msg):
		self.logs.append(msg)
	def info(self, msg):
		self.logs.append(msg)
	def warning(self, msg):
		self.logs.append(msg)
	def error(self, msg):
		self.logs.append(msg)

class DummyRequest(ICLIRequest):
	def all(self):
		return {"foo": "bar"}
	def argument(self, name):
		return None
	def command(self):
		return "dummy_command"

class DummyConsole(IConsole):
	def __init__(self):
		self.output = []
	def newLine(self):
		self.output.append("\n")
	def exception(self, exc):
		self.output.append(f"Exception: {exc}")
	def anticipate(self, *args, **kwargs):
		pass
	def ask(self, *args, **kwargs):
		return ""
	def choice(self, *args, **kwargs):
		return ""
	def clear(self):
		pass
	def clearLine(self):
		pass
	def confirm(self, *args, **kwargs):
		return True
	def error(self, msg):
		self.output.append(f"Error: {msg}")
	def exitError(self, *args, **kwargs):
		pass
	def exitSuccess(self, *args, **kwargs):
		pass
	def fail(self, msg):
		self.output.append(f"Fail: {msg}")
	def info(self, msg):
		self.output.append(f"Info: {msg}")
	def line(self, msg=""):
		self.output.append(msg)
	def secret(self, *args, **kwargs):
		return ""
	def success(self, msg):
		self.output.append(f"Success: {msg}")
	def table(self, *args, **kwargs):
		pass
	def textError(self, msg):
		return f"[ERROR] {msg}"
	def textErrorBold(self, msg):
		return f"[ERROR BOLD] {msg}"
	def textInfo(self, msg):
		return f"[INFO] {msg}"
	def textInfoBold(self, msg):
		return f"[INFO BOLD] {msg}"
	def textMuted(self, msg):
		return f"[MUTED] {msg}"
	def textMutedBold(self, msg):
		return f"[MUTED BOLD] {msg}"
	def textSuccess(self, msg):
		return f"[SUCCESS] {msg}"
	def textSuccessBold(self, msg):
		return f"[SUCCESS BOLD] {msg}"
	def textUnderline(self, msg):
		return f"[UNDERLINE] {msg}"
	def textWarning(self, msg):
		return f"[WARNING] {msg}"
	def textWarningBold(self, msg):
		return f"[WARNING BOLD] {msg}"
	def warning(self, msg):
		self.output.append(f"Warning: {msg}")
	def write(self, msg):
		self.output.append(msg)
	def writeLine(self, msg=""):
		self.output.append(f"{msg}\n")

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
