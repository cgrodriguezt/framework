from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.console.contracts.command import ICommand
from orionis.console.fluent.command import Command
from orionis.console.args.argument import CLIArgument
from orionis.test.cases.synchronous import SyncTestCase

class DummyCommand:

    def handle(self):
        """
        Executes the main logic for the command.

        Returns
        -------
        str
            The string "handled", indicating that the handle action was performed successfully.
        """
        return "handled"

    def custom(self):
        """
        Returns a string indicating a custom action.

        Returns
        -------
        str
            The string "custom", indicating that a custom action was performed.
        """
        return "custom"

class TestConsoleFluentCommand(SyncTestCase):

	def testValidConstruction(self):
		"""
		Test that a Command can be constructed with valid parameters.

		Returns
		-------
		None
			Asserts that no exception is raised and the object is created.
		"""
		cmd = Command('foo:bar', DummyCommand, 'handle')
		self.assertIsInstance(cmd, Command)

	def testInvalidConcreteRaisesTypeError(self):
		"""
		Test that providing a non-class as concrete raises TypeError.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		try:
			Command('foo:bar', DummyCommand(), 'handle')
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-class concrete.")

	def testInvalidMethodRaisesTypeError(self):
		"""
		Test that providing a non-string as method raises TypeError.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		try:
			Command('foo:bar', DummyCommand, 123)
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-string method.")

	def testNonexistentMethodRaisesAttributeError(self):
		"""
		Test that providing a method name that does not exist raises AttributeError.

		Returns
		-------
		None
			Asserts that AttributeError is raised.
		"""
		try:
			Command('foo:bar', DummyCommand, 'notfound')
		except AttributeError:
			pass
		else:
			self.fail("AttributeError not raised for nonexistent method.")

	def testTimestampSetter(self):
		"""
		Test that the timestamp method sets the flag and supports chaining.

		Returns
		-------
		None
			Asserts that the method returns self and does not raise.
		"""
		cmd = Command('foo:bar', DummyCommand, 'handle')
		result = cmd.timestamp(False)
		self.assertIs(result, cmd)

	def testTimestampSetterTypeError(self):
		"""
		Test that timestamp method raises TypeError for non-bool input.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		cmd = Command('foo:bar', DummyCommand, 'handle')
		try:
			cmd.timestamp('yes')
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-bool timestamp.")

	def testDescriptionSetter(self):
		"""
		Test that the description method sets the description and supports chaining.

		Returns
		-------
		None
			Asserts that the method returns self and does not raise.
		"""
		cmd = Command('foo:bar', DummyCommand, 'handle')
		result = cmd.description("A test command.")
		self.assertIs(result, cmd)

	def testDescriptionSetterTypeError(self):
		"""
		Test that description method raises TypeError for non-string input.

		Returns
		-------
		None
			Asserts that TypeError is raised.
		"""
		cmd = Command('foo:bar', DummyCommand, 'handle')
		try:
			cmd.description(123)
		except TypeError:
			pass
		else:
			self.fail("TypeError not raised for non-string description.")

	def testArgumentsSetter(self):
		"""
		Test that the arguments method sets arguments and supports chaining.

		Returns
		-------
		None
			Asserts that the method returns self and does not raise.
		"""
		arg = CLIArgument(flags='foo', type=str)
		cmd = Command('foo:bar', DummyCommand, 'handle')
		result = cmd.arguments([arg])
		self.assertIs(result, cmd)

	def testArgumentsSetterTypeError(self):
		"""
		Test that arguments method raises TypeError for invalid input types.

		Returns
		-------
		None
			Asserts that TypeError is raised for non-list or non-CLIArgument elements.
		"""
		cmd = Command('foo:bar', DummyCommand, 'handle')
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

	def testGetReturnsTuple(self):
		"""
		Test that get returns a tuple with signature and CommandEntity.

		Returns
		-------
		None
			Asserts that the return value is a tuple and the first element is the signature.
		"""
		arg = CLIArgument(flags='foo', type=str)
		cmd = Command('foo:bar', DummyCommand, 'handle').arguments([arg])
		result = cmd.get()
		self.assertIsInstance(result, tuple)
		self.assertEqual(result[0], 'foo:bar')

	def testImplementation(self):
		"""
		Checks that all methods declared in the `ICommand` interface are implemented
		by the `Command` concrete class.

		Uses reflection to obtain method names from both the interface and its implementation,
		then verifies that each interface method exists in the concrete class.

		Parameters
		----------
		None

		Returns
		-------
		None
			Raises AssertionError if any interface method is missing from the concrete class.
		"""
		# Get all method names from the ICommand interface using reflection
		rf_abstract = ReflectionAbstract(ICommand).getMethods()

		# Get all method names from the Command implementation using reflection
		rf_concrete = ReflectionConcrete(Command).getMethods()

		# Check that every interface method is present in the implementation
		for method in rf_abstract:
			self.assertIn(method, rf_concrete)  # Assert method exists in concrete class

	def testPropierties(self):
		"""
		Checks that all properties declared in the `ICommand` interface are implemented
		by the `Command` concrete class.

		Uses reflection to obtain property names from both the interface and its implementation,
		then verifies that each interface property exists in the concrete class.

		Parameters
		----------
		None

		Returns
		-------
		None
			Raises AssertionError if any interface property is missing from the concrete class.
		"""
		# Get all property names from the ICommand interface using reflection
		rf_abstract = ReflectionAbstract(ICommand).getProperties()

		# Get all property names from the Command implementation using reflection
		rf_concrete = ReflectionConcrete(Command).getProperties()

		# Check that every interface property is present in the implementation
		for prop in rf_abstract:
			self.assertIn(prop, rf_concrete)  # Assert property exists in concrete class
