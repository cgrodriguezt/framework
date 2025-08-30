
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.fluent.command import Command
from orionis.console.args.argument import CLIArgument
from tests.console.fluent.dummy.dummy_concrete import DummyConcrete

class TestCommand(AsyncTestCase):

	async def testValidConstruction(self):
		"""
		Test that a Command can be constructed with valid parameters.

		Returns
		-------
		None
			Asserts that no exception is raised and the object is created.
		"""
		cmd = Command('foo:bar', DummyConcrete, 'handle')
		self.assertIsInstance(cmd, Command)

	async def testInvalidConcreteRaisesTypeError(self):
		"""
		Test that providing a non-class as concrete raises TypeError.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		try:
			Command('foo:bar', DummyConcrete(), 'handle')
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-class concrete.")

	async def testInvalidMethodRaisesTypeError(self):
		"""
		Test that providing a non-string as method raises TypeError.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		try:
			Command('foo:bar', DummyConcrete, 123)
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-string method.")

	async def testNonexistentMethodRaisesAttributeError(self):
		"""
		Test that providing a method name that does not exist raises AttributeError.

		Returns
		-------
		None
			Asserts that AttributeError is raised.
		"""
		try:
			Command('foo:bar', DummyConcrete, 'notfound')
		except AttributeError:
			pass
		else:
			self.fail("AttributeError not raised for nonexistent method.")

	async def testTimestampSetter(self):
		"""
		Test that the timestamp method sets the flag and supports chaining.

		Returns
		-------
		None
			Asserts that the method returns self and does not raise.
		"""
		cmd = Command('foo:bar', DummyConcrete, 'handle')
		result = cmd.timestamp(False)
		self.assertIs(result, cmd)

	async def testTimestampSetterTypeError(self):
		"""
		Test that timestamp method raises TypeError for non-bool input.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		cmd = Command('foo:bar', DummyConcrete, 'handle')
		try:
			cmd.timestamp('yes')
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-bool timestamp.")

	async def testDescriptionSetter(self):
		"""
		Test that the description method sets the description and supports chaining.

		Returns
		-------
		None
			Asserts that the method returns self and does not raise.
		"""
		cmd = Command('foo:bar', DummyConcrete, 'handle')
		result = cmd.description("A test command.")
		self.assertIs(result, cmd)

	async def testDescriptionSetterTypeError(self):
		"""
		Test that description method raises TypeError for non-string input.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		cmd = Command('foo:bar', DummyConcrete, 'handle')
		try:
			cmd.description(123)
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-string description.")

	async def testArgumentsSetter(self):
		"""
		Test that the arguments method sets arguments and supports chaining.

		Returns
		-------
		None
			Asserts that the method returns self and does not raise.
		"""
		arg = CLIArgument(flags='foo', type=str)
		cmd = Command('foo:bar', DummyConcrete, 'handle')
		result = cmd.arguments([arg])
		self.assertIs(result, cmd)

	async def testArgumentsSetterTypeError(self):
		"""
		Test that arguments method raises TypeError for invalid input types.

		Returns
		-------
		None
			Asserts that TypeError is raised for non-list or non-CLIArgument elements.
		"""
		cmd = Command('foo:bar', DummyConcrete, 'handle')
		# Not a list
		try:
			cmd.arguments('notalist')
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-list arguments.")
		# List with invalid element
		try:
			cmd.arguments([123])
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-CLIArgument in arguments.")

	async def testGetReturnsTuple(self):
		"""
		Test that get returns a tuple with signature and CommandEntity.

		Returns
		-------
		None
			Asserts that the return value is a tuple and the first element is the signature.
		"""
		arg = CLIArgument(flags='foo', type=str)
		cmd = Command('foo:bar', DummyConcrete, 'handle').arguments([arg])
		result = cmd.get()
		self.assertIsInstance(result, tuple)
		self.assertEqual(result[0], 'foo:bar')
