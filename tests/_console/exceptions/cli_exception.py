from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.exceptions.cli_exceptions import (
	CLIOrionisException,
	CLIOrionisValueError,
	CLIOrionisRuntimeError,
	CLIOrionisScheduleException,
	CLIOrionisTypeError
)

class TestCLIExceptions(AsyncTestCase):
	"""
	Test suite for custom CLI exceptions in Orionis.
	"""

	async def testCliOrionisException(self):
		"""
		Test that CLIOrionisException can be raised and caught.

		Raises
		------
		AssertionError
			If the exception is not raised or the message is incorrect.
		"""
		msg = "Test CLIOrionisException"
		try:
			raise CLIOrionisException(msg)
		except CLIOrionisException as e:
			self.assertEqual(str(e), msg)
		else:
			self.fail("CLIOrionisException was not raised.")

	async def testCliOrionisValueError(self):
		"""
		Test that CLIOrionisValueError can be raised and caught.

		Raises
		------
		AssertionError
			If the exception is not raised or the message is incorrect.
		"""
		msg = "Test CLIOrionisValueError"
		try:
			raise CLIOrionisValueError(msg)
		except CLIOrionisValueError as e:
			self.assertEqual(str(e), msg)
		else:
			self.fail("CLIOrionisValueError was not raised.")

	async def testCliOrionisRuntimeError(self):
		"""
		Test that CLIOrionisRuntimeError can be raised and caught.

		Raises
		------
		AssertionError
			If the exception is not raised or the message is incorrect.
		"""
		msg = "Test CLIOrionisRuntimeError"
		try:
			raise CLIOrionisRuntimeError(msg)
		except CLIOrionisRuntimeError as e:
			self.assertEqual(str(e), msg)
		else:
			self.fail("CLIOrionisRuntimeError was not raised.")

	async def testCliOrionisScheduleException(self):
		"""
		Test that CLIOrionisScheduleException can be raised and caught.

		Raises
		------
		AssertionError
			If the exception is not raised or the message is incorrect.
		"""
		msg = "Test CLIOrionisScheduleException"
		try:
			raise CLIOrionisScheduleException(msg)
		except CLIOrionisScheduleException as e:
			self.assertEqual(str(e), msg)
		else:
			self.fail("CLIOrionisScheduleException was not raised.")

	async def testCliOrionisTypeError(self):
		"""
		Test that CLIOrionisTypeError can be raised and caught.

		Raises
		------
		AssertionError
			If the exception is not raised or the message is incorrect.
		"""
		msg = "Test CLIOrionisTypeError"
		try:
			raise CLIOrionisTypeError(msg)
		except CLIOrionisTypeError as e:
			self.assertEqual(str(e), msg)
		else:
			self.fail("CLIOrionisTypeError was not raised.")
