
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_cLI_request import DummyCLIRequest

class TestICLIRequest(AsyncTestCase):
	async def testCommandReturnsCorrectValue(self):
		"""
		Test that the command() method returns the correct command string.

		Returns
		-------
		None
		"""
		req = DummyCLIRequest("runserver")
		assert req.command() == "runserver"

	async def testAllReturnsArgumentsDict(self):
		"""
		Test that all() returns the full arguments dictionary.

		Returns
		-------
		None
		"""
		args = {"foo": 1, "bar": 2}
		req = DummyCLIRequest("cmd", args)
		assert req.all() == args

	async def testArgumentReturnsValueOrDefault(self):
		"""
		Test that argument() returns the correct value or the default if not present.

		Returns
		-------
		None
		"""
		args = {"alpha": 42}
		req = DummyCLIRequest("cmd", args)
		assert req.argument("alpha") == 42
		assert req.argument("beta") is None
		assert req.argument("beta", default=99) == 99

	async def testGetCWDReturnsCurrentDirectory(self):
		"""
		Test that getCWD() returns the current working directory as a string.

		Returns
		-------
		None
		"""
		req = DummyCLIRequest("cmd")
		import os
		assert req.getCWD() == os.getcwd()

	async def testGetPIDReturnsProcessID(self):
		"""
		Test that getPID() returns the current process ID as an integer.

		Returns
		-------
		None
		"""
		req = DummyCLIRequest("cmd")
		import os
		assert req.getPID() == os.getpid()

	async def testGetParentPIDReturnsParentProcessID(self):
		"""
		Test that getParentPID() returns the parent process ID as an integer.

		Returns
		-------
		None
		"""
		req = DummyCLIRequest("cmd")
		import os
		assert req.getParentPID() == os.getppid()

	async def testGetExecutableReturnsPythonPath(self):
		"""
		Test that getExecutable() returns the path to the Python executable.

		Returns
		-------
		None
		"""
		req = DummyCLIRequest("cmd")
		import sys
		assert req.getExecutable() == sys.executable

	async def testGetPlatformReturnsSystemName(self):
		"""
		Test that getPlatform() returns the current operating system name.

		Returns
		-------
		None
		"""
		req = DummyCLIRequest("cmd")
		import platform
		assert req.getPlatform() == platform.system()
