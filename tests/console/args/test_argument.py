from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.console.args.argument import CLIArgument
from orionis.console.enums.actions import ArgumentAction
from orionis.console.exceptions import CLIOrionisValueError

class TestCLIArgument(AsyncTestCase):

    async def testValidArgument(self):
        """
        Test that a CLIArgument instance is correctly initialized with valid parameters.

        This test verifies that when a CLIArgument is created with typical valid flags, type, and help text, all attributes are set as expected, including the default action.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of CLIArgument initialization.
        """

        # Create a CLIArgument with valid flags, type, and help text
        arg = CLIArgument(flags=["--export", "-e"], type=str, help="Export file")

        # Assert that the flags are set correctly
        self.assertEqual(arg.flags, ["--export", "-e"])

        # Assert that the type is set correctly
        self.assertEqual(arg.type, str)

        # Assert that the help text is set correctly
        self.assertEqual(arg.help, "Export file")

        # Assert that the default action is set to STORE
        self.assertEqual(arg.action, ArgumentAction.STORE.value)

    async def testInvalidFlags(self):
        """
        Test that CLIArgument raises an error when provided with invalid flags.

        This test ensures that passing an empty list of flags to CLIArgument triggers a CLIOrionisValueError, enforcing the requirement for at least one flag.

        Returns
        -------
        None
            This method does not return a value. It asserts that an exception is raised for invalid flags.
        """

        # Attempt to create a CLIArgument with empty flags and expect an error
        with self.assertRaises(CLIOrionisValueError):
            CLIArgument(flags=[], type=str)

    async def testDefaultValue(self):
        """
        Test that the default value is correctly assigned in CLIArgument.

        This test checks that when a default value is provided to CLIArgument, it is stored and accessible as expected.

        Returns
        -------
        None
            This method does not return a value. It asserts the correct assignment of the default value.
        """

        # Create a CLIArgument with a default value
        arg = CLIArgument(flags=["--count"], type=int, default=5)

        # Assert that the default value is set correctly
        self.assertEqual(arg.default, 5)

    async def testTypeValidation(self):
        """
        Test that CLIArgument enforces type validation for choices.

        This test ensures that if the choices provided to CLIArgument do not all match the specified type, a CLIOrionisValueError is raised.

        Returns
        -------
        None
            This method does not return a value. It asserts that an exception is raised for invalid choice types.
        """

        # Attempt to create a CLIArgument with choices of mixed types and expect an error
        with self.assertRaises(CLIOrionisValueError):
            CLIArgument(flags=["--mode"], type=int, choices=[1, "two", 3])

    async def testBooleanFlag(self):
        """
        Test that boolean flags are auto-configured with the correct action and type.

        This test verifies that when a CLIArgument is created with type bool, the action is set to STORE_TRUE and the type is set to None for compatibility with argument parsers.

        Returns
        -------
        None
            This method does not return a value. It asserts correct auto-configuration for boolean flags.
        """

        # Create a CLIArgument with a boolean type
        arg = CLIArgument(flags=["--force"], type=bool, default=False)

        # Assert that the action is set to STORE_TRUE for boolean flags
        self.assertEqual(arg.action, ArgumentAction.STORE_TRUE.value)

        # Assert that the type is set to None for boolean flags
        self.assertIsNone(arg.type)

    async def testListArgument(self):
        """
        Test that list type arguments are configured with correct nargs and type.

        This test ensures that when a CLIArgument is created with type list, it is configured with nargs set to '+' and type set to str for compatibility with argument parsers.

        Returns
        -------
        None
            This method does not return a value. It asserts correct configuration for list type arguments.
        """

        # Create a CLIArgument with a list type
        arg = CLIArgument(flags=["--items"], type=list)

        # Assert that nargs is set to '+' for list arguments
        self.assertEqual(arg.nargs, "+")

        # Assert that the type is set to str for list arguments
        self.assertEqual(arg.type, str)

    async def testEdgeCaseDuplicateFlags(self):
        """
        Test that providing duplicate flags raises an error in CLIArgument.

        This test ensures that if duplicate flags are provided in the flags list, CLIOrionisValueError is raised to prevent ambiguous argument definitions.

        Returns
        -------
        None
            This method does not return a value. It asserts that an exception is raised for duplicate flags.
        """

        # Attempt to create a CLIArgument with duplicate flags and expect an error
        with self.assertRaises(CLIOrionisValueError):
            CLIArgument(flags=["--foo", "--foo"], type=str)

    async def testInvalidType(self):
        """
        Test that providing an invalid type raises an error in CLIArgument.

        This test checks that if a non-type object is passed as the type argument, CLIOrionisValueError is raised, enforcing type safety.

        Returns
        -------
        None
            This method does not return a value. It asserts that an exception is raised for invalid type arguments.
        """

        # Attempt to create a CLIArgument with an invalid type and expect an error
        with self.assertRaises(CLIOrionisValueError):
            CLIArgument(flags=["--bar"], type="not_a_type")

    async def testAutoGeneratedHelpAndMetavar(self):
        """
        Test that help and metavar fields are auto-generated when not provided.

        This test verifies that if help and metavar are omitted, CLIArgument generates them based on the flag name, ensuring user-friendly defaults.

        Returns
        -------
        None
            This method does not return a value. It asserts correct auto-generation of help and metavar fields.
        """

        # Create a CLIArgument without specifying help or metavar
        arg = CLIArgument(flags=["--long-flag"], type=str)

        # Assert that the help text is auto-generated and starts with a capitalized version of the flag
        self.assertTrue(arg.help.startswith("Long Flag"))

        # Assert that the metavar is auto-generated in uppercase with underscores
        self.assertEqual(arg.metavar, "LONG_FLAG")