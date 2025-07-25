import asyncio
from orionis.console.base.command import BaseCommand
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.base.mock_command import CustomCommandWithoutHandle, CustomCommandComplete

class TestBaseCommand(AsyncTestCase):

    async def testCommandHandleNotImplemented(self):
        """
        Tests that invoking the 'handle' method on a command class without an implementation raises NotImplementedError.

        This method creates an instance of a command class that does not override the 'handle' method.
        It then attempts to call 'handle', checking whether it is a coroutine or a regular function,
        and verifies that a NotImplementedError is raised in both cases.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            The test passes if NotImplementedError is raised when 'handle' is called.

        Raises
        ------
        AssertionError
            If NotImplementedError is not raised when expected.
        """
        command = CustomCommandWithoutHandle()

        # Check if 'handle' is asynchronous or synchronous and assert NotImplementedError is raised
        with self.assertRaises(NotImplementedError):

            # Await if 'handle' is a coroutine function
            if asyncio.iscoroutinefunction(command.handle):
                await command.handle()

            # Call directly if 'handle' is a regular function
            else:
                command.handle()

    async def testCommandHandleSuccess(self):
        """
        Tests the successful execution of the 'handle' method in CustomCommandComplete.

        This method creates an instance of CustomCommandComplete and invokes its asynchronous 'handle' method.
        It verifies that the returned value matches the expected success message.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            The test passes if the returned value from 'handle' is "Finished Successfully".

        Raises
        ------
        AssertionError
            If the returned value does not match the expected message.
        """

        # Create an instance of the command with a complete handle implementation
        command = CustomCommandComplete()

        # Await the asynchronous handle method and capture the result
        result = await command.handle()

        # Assert that the result matches the expected success message
        self.assertEqual(result, "Finished Successfully")

    async def testIsSubclassOfBaseCommand(self):
        """
        Checks whether CustomCommandComplete and CustomCommandWithoutHandle are subclasses of BaseCommand.

        This test verifies that both custom command classes directly inherit from the BaseCommand class,
        ensuring proper class hierarchy and adherence to the command interface.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            The test passes if both classes are found to be subclasses of BaseCommand.

        Raises
        ------
        AssertionError
            If either CustomCommandComplete or CustomCommandWithoutHandle does not inherit from BaseCommand.
        """

        # Assert that CustomCommandComplete inherits from BaseCommand
        self.assertIn(BaseCommand, CustomCommandComplete.__bases__)

        # Assert that CustomCommandWithoutHandle inherits from BaseCommand
        self.assertIn(BaseCommand, CustomCommandWithoutHandle.__bases__)

    async def testGetArgs(self):
        """
        Verifies that the 'args' property of command classes returns the expected dictionary of arguments.

        This test checks that the 'args' property of both CustomCommandComplete and CustomCommandWithoutHandle
        matches the predefined dictionary of expected argument values. It ensures that the command classes
        correctly expose their arguments as specified.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            The test passes if the 'args' property of both command classes equals the expected dictionary.

        Raises
        ------
        AssertionError
            If the 'args' property does not match the expected dictionary for either command class.
        """

        # Define the expected arguments dictionary
        expected_args = {
            'key_str': 'example_value',
            'key_int': 42,
            'key_float': 3.14,
            'key_bool': True,
            'key_list': [1, 2, 3],
            'key_dict': {'nested_key': 'nested_value'}
        }

        # Create an instance of CustomCommandComplete and check its args property
        command = CustomCommandComplete()
        self.assertEqual(command.args, expected_args)

        # Create an instance of CustomCommandWithoutHandle and check its args property
        command2 = CustomCommandWithoutHandle()
        self.assertEqual(command2.args, expected_args)

    async def testArgsTypes(self):
        """
        Validates the types of values in the 'args' property of CustomCommandComplete.

        This test checks that each key in the 'args' dictionary corresponds to a value of the expected type.
        It ensures that the command's argument definitions conform to the required data types.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            The test passes if all argument types match their expected Python types.

        Raises
        ------
        AssertionError
            If any argument value does not match its expected type.
        """

        # Create an instance of the command to access its arguments
        command = CustomCommandComplete()
        args = command.args

        # Assert the type of each argument value
        self.assertIsInstance(args['key_str'], str)      # Should be a string
        self.assertIsInstance(args['key_int'], int)      # Should be an integer
        self.assertIsInstance(args['key_float'], float)  # Should be a float
        self.assertIsInstance(args['key_bool'], bool)    # Should be a boolean
        self.assertIsInstance(args['key_list'], list)    # Should be a list
        self.assertIsInstance(args['key_dict'], dict)    # Should be a dictionary

    async def testHandleIsAsync(self):
        """
        Checks whether the 'handle' method of CustomCommandComplete is defined as an asynchronous coroutine.

        This test verifies that the 'handle' method in CustomCommandComplete is implemented as a coroutine function,
        ensuring that it can be awaited and supports asynchronous execution.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            The test passes if 'handle' is a coroutine function; otherwise, it fails with an assertion error.

        Raises
        ------
        AssertionError
            If 'handle' is not a coroutine function.
        """
        # Assert that the 'handle' method is a coroutine function (async def)
        self.assertTrue(asyncio.iscoroutinefunction(CustomCommandComplete.handle))
