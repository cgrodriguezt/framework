from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.failure.contracts.handler import IBaseExceptionHandler
from orionis.services.log.contracts.log_service import ILogger
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.console import IConsole
import types

class DummyThrowable:
    def __init__(self, type_, message, args, traceback):
        self.type = type_
        self.message = message
        self.args = args
        self.traceback = traceback

class DummyLogger(ILogger):
    def __init__(self):
        self.logged = []
    async def log(self, msg):
        self.logged.append(msg)
    async def debug(self, msg):
        self.logged.append(f"DEBUG: {msg}")
    async def info(self, msg):
        self.logged.append(f"INFO: {msg}")
    async def warning(self, msg):
        self.logged.append(f"WARNING: {msg}")
    async def error(self, msg):
        self.logged.append(f"ERROR: {msg}")

class DummyRequest(ICLIRequest):
    def all(self):
        return {}

    def argument(self, name, default=None):
        return default

    def command(self):
        return "dummy_command"

class DummyConsole(IConsole):
    def __init__(self):
        self.output = []
    async def write(self, msg):
        self.output.append(msg)

class DummyExceptionHandler(IBaseExceptionHandler):
    async def destructureException(self, e: BaseException):
        return DummyThrowable(type(e), str(e), e.args, 'dummy_traceback')
    async def shouldIgnoreException(self, e: BaseException) -> bool:
        return isinstance(e, KeyboardInterrupt)
    async def report(self, exception: BaseException, log: ILogger):
        await log.log(f"Reported: {exception}")
    async def renderCLI(self, exception: BaseException, request: ICLIRequest, log: ILogger, console: IConsole):
        await console.write(f"Exception: {exception}")

class TestIBaseExceptionHandler(AsyncTestCase):
    async def testDestructureException(self):
        """
        Test that destructureException returns a structured Throwable object.

        Returns
        -------
        None
        """
        handler = DummyExceptionHandler()
        exc = ValueError("Test error", 123)
        throwable = await handler.destructureException(exc)
        self.assertEqual(throwable.type, ValueError)
        self.assertEqual(throwable.message, "Test error")
        self.assertEqual(throwable.args, ("Test error", 123))
        self.assertEqual(throwable.traceback, 'dummy_traceback')

    async def testShouldIgnoreException(self):
        """
        Test that shouldIgnoreException returns True for KeyboardInterrupt and False otherwise.

        Returns
        -------
        None
        """
        handler = DummyExceptionHandler()
        self.assertTrue(await handler.shouldIgnoreException(KeyboardInterrupt()))
        self.assertFalse(await handler.shouldIgnoreException(ValueError()))

    async def testReport(self):
        """
        Test that report logs the exception using the provided logger.

        Returns
        -------
        None
        """
        handler = DummyExceptionHandler()
        logger = DummyLogger()
        exc = RuntimeError("Something went wrong")
        await handler.report(exc, logger)
        self.assertIn("Reported: Something went wrong", logger.logged)

    async def testRenderCLI(self):
        """
        Test that renderCLI writes the exception message to the console.

        Returns
        -------
        None
        """
        handler = DummyExceptionHandler()
        logger = DummyLogger()
        request = DummyRequest()
        console = DummyConsole()
        exc = Exception("CLI error")
        await handler.renderCLI(exc, request, logger, console)
        self.assertIn("Exception: CLI error", console.output)
