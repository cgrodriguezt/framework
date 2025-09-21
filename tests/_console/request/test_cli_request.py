from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.request.cli_request import CLIRequest
from orionis.console.exceptions import CLIOrionisValueError

class TestCLIRequest(AsyncTestCase):

	async def testFromListWithKeyValueArguments(self):
		"""
		Test CLIRequest.fromList with key-value arguments.

		Ensures that arguments in the form '--key=value' are parsed correctly.
		"""
		args = ['migrate', '--database=production', '--force', 'users']
		req = CLIRequest.fromList(args)
		self.assertEqual(req.command(), 'migrate')
		self.assertEqual(req.argument('database'), 'production')
		self.assertEqual(req.argument('force'), 'force')
		self.assertEqual(req.argument('users'), 'users')

	async def testFromListWithEmptyList(self):
		"""
		Test CLIRequest.fromList with an empty argument list.

		Ensures that the default command name is used and arguments are empty.
		"""
		req = CLIRequest.fromList([])
		self.assertEqual(req.command(), '__unknown__')
		self.assertEqual(req.all(), {})

	async def testFromListWithInvalidType(self):
		"""
		Test CLIRequest.fromList with invalid argument type.

		Ensures that a CLIOrionisValueError is raised when input is not a list.
		"""
		with self.assertRaises(CLIOrionisValueError):
			CLIRequest.fromList('notalist')

	async def testArgumentDefaultValue(self):
		"""
		Test CLIRequest.argument with a missing key and default value.

		Ensures that the default value is returned when the argument is missing.
		"""
		args = ['run']
		req = CLIRequest.fromList(args)
		self.assertEqual(req.argument('missing', default='default'), 'default')

	async def testGetCWDReturnsString(self):
		"""
		Test CLIRequest.getCWD returns a string path.

		Ensures that the current working directory is returned as a string.
		"""
		req = CLIRequest('cmd', {})
		cwd = req.getCWD()
		self.assertIsInstance(cwd, str)
		self.assertTrue(len(cwd) > 0)

	async def testGetPIDReturnsInt(self):
		"""
		Test CLIRequest.getPID returns an integer.

		Ensures that the process ID is returned as an integer value.
		"""
		req = CLIRequest('cmd', {})
		pid = req.getPID()
		self.assertIsInstance(pid, int)
		self.assertTrue(pid > 0)

	async def testGetParentPIDReturnsInt(self):
		"""
		Test CLIRequest.getParentPID returns an integer.

		Ensures that the parent process ID is returned as an integer value.
		"""
		req = CLIRequest('cmd', {})
		ppid = req.getParentPID()
		self.assertIsInstance(ppid, int)
		self.assertTrue(ppid > 0)

	async def testGetExecutableReturnsString(self):
		"""
		Test CLIRequest.getExecutable returns a string path.

		Ensures that the Python executable path is returned as a string.
		"""
		req = CLIRequest('cmd', {})
		exe = req.getExecutable()
		self.assertIsInstance(exe, str)
		self.assertTrue(len(exe) > 0)

	async def testGetPlatformReturnsString(self):
		"""
		Test CLIRequest.getPlatform returns a string.

		Ensures that the platform name is returned as a string value.
		"""
		req = CLIRequest('cmd', {})
		platform = req.getPlatform()
		self.assertIsInstance(platform, str)
		self.assertTrue(len(platform) > 0)
