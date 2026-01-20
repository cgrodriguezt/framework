from orionis.console.request.cli_request import CLIRequest
from orionis.console.exceptions import CLIOrionisValueError
from orionis.test.cases.synchronous import SyncTestCase

class TestConsoleRequest(SyncTestCase):

	def testFromListWithKeyValueArguments(self):
		"""
		Tests CLIRequest.fromList for correct parsing of key-value, flag, and positional arguments.

		This method verifies that CLIRequest.fromList can accurately parse:
		- Key-value arguments in the form '--key=value'.
		- Flag arguments (e.g., '--force') where the key maps to itself.
		- Positional arguments, which are accessible by their value as key.
		The command name should be set to the first argument in the list.

		Parameters
		----------
		self : TestCLIRequest
			The test case instance.

		Returns
		-------
		None
			The method does not return any value. Assertions are used to validate correctness.

		Notes
		-----
		- Key-value pairs should result in the key mapping to its value.
		- Flags should map the key to its own name.
		- Positional arguments should be accessible using their value as the key.
		- The command name is expected to be the first argument in the list.
		"""
		args = ["migrate", "--database=production", "--force", "users"]
		# Create a CLIRequest instance from the argument list
		req = CLIRequest.fromList(args)
		# Assert that the command is correctly identified
		self.assertEqual(req.command(), "migrate")
		# Assert that key-value argument is parsed correctly
		self.assertEqual(req.argument("database"), "production")
		# Assert that flag argument is parsed with its own name as value
		self.assertEqual(req.argument("force"), "force")
		# Assert that positional argument is accessible
		self.assertEqual(req.argument("users"), "users")

	def testFromListWithEmptyList(self):
		"""
		Tests CLIRequest.fromList with an empty argument list.

		Ensures that when an empty list is provided, the default command name is used and no arguments are present.

		Parameters
		----------
		self : TestCLIRequest
			The test case instance.

		Returns
		-------
		None
			The method does not return any value. Assertions are used to validate correctness.
		"""
		req = CLIRequest.fromList([])
		# Assert that the default command name is set
		self.assertEqual(req.command(), "__unknown__")
		# Assert that no arguments are present
		self.assertEqual(req.arguments(), {})

	def testFromListWithInvalidType(self):
		"""
		Tests CLIRequest.fromList with an invalid argument type.

		Verifies that a CLIOrionisValueError is raised when the input is not a list.

		Parameters
		----------
		self : TestCLIRequest
			The test case instance.

		Returns
		-------
		None
			The method does not return any value. Assertions are used to validate correctness.
		"""
		# Assert that passing a non-list raises the expected exception
		with self.assertRaises(CLIOrionisValueError):
			CLIRequest.fromList("notalist")

	def testArgumentDefaultValue(self):
		"""
		Tests CLIRequest.argument for returning a default value when the key is missing.

		Ensures that if the requested argument key does not exist, the provided default value is returned.

		Parameters
		----------
		self : TestCLIRequest
			The test case instance.

		Returns
		-------
		None
			The method does not return any value. Assertions are used to validate correctness.
		"""
		args = ["run"]
		req = CLIRequest.fromList(args)
		# Assert that the default value is returned for a missing key
		self.assertEqual(req.argument("missing", default="default"), "default")
