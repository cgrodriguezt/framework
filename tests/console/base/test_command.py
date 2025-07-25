import asyncio
from orionis.console.base.command import BaseCommand
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.base.mock_command import CustomCommandWithoutHandle, CustomCommandComplete

class TestBaseCommand(AsyncTestCase):

    async def testCommandHandleNotImplemented(self):
        """
        Checks that a NotImplementedError is raised if the 'handle' method is not implemented in the command.

        This test instantiates a command class that does not override the 'handle' method and verifies
        that calling 'handle' raises a NotImplementedError, regardless of whether 'handle' is synchronous or asynchronous.

        Returns:
            None. The test passes if NotImplementedError is raised as expected.
        """
        command = CustomCommandWithoutHandle()
        # Assert that calling handle raises NotImplementedError
        with self.assertRaises(NotImplementedError):
            if asyncio.iscoroutinefunction(command.handle):
                await command.handle()
            else:
                command.handle()

    async def testCommandHandleSuccess(self):
        """
        Verifies that the 'handle' method of CustomCommandComplete returns the expected message.

        This test calls the asynchronous 'handle' method and checks that the return value matches the expected string.

        Returns:
            None. The test passes if the returned message is "Finished Successfully".
        """
        command = CustomCommandComplete()
        result = await command.handle()
        self.assertEqual(result, "Finished Successfully")

    async def testIsSubclassOfBaseCommand(self):
        """
        Checks that CustomCommandComplete and CustomCommandWithoutHandle are subclasses of BaseCommand.

        This ensures that both custom command classes inherit from the base command class.

        Returns:
            None. The test passes if both classes are subclasses of BaseCommand.
        """
        self.assertIn(BaseCommand, CustomCommandComplete.__bases__)
        self.assertIn(BaseCommand, CustomCommandWithoutHandle.__bases__)

    async def testGetArgs(self):
        """
        Verifies that the 'args' property returns the expected dictionary of arguments.

        This test checks that the 'args' property of both command classes matches the predefined dictionary.

        Returns:
            None. The test passes if the 'args' property equals the expected dictionary.
        """
        expected_args = {
            'key_str': 'example_value',
            'key_int': 42,
            'key_float': 3.14,
            'key_bool': True,
            'key_list': [1, 2, 3],
            'key_dict': {'nested_key': 'nested_value'}
        }
        command = CustomCommandComplete()
        # Check that args property matches expected_args
        self.assertEqual(command.args, expected_args)
        command2 = CustomCommandWithoutHandle()
        self.assertEqual(command2.args, expected_args)

    async def testArgsTypes(self):
        """
        Checks the types of the values in the 'args' property.

        This test ensures that each value in the 'args' dictionary has the correct type.

        Returns:
            None. The test passes if all types match the expected types.
        """
        command = CustomCommandComplete()
        args = command.args
        # Assert the type of each argument
        self.assertIsInstance(args['key_str'], str)
        self.assertIsInstance(args['key_int'], int)
        self.assertIsInstance(args['key_float'], float)
        self.assertIsInstance(args['key_bool'], bool)
        self.assertIsInstance(args['key_list'], list)
        self.assertIsInstance(args['key_dict'], dict)

    async def testHandleIsAsync(self):
        """
        Checks that the 'handle' method of CustomCommandComplete is an asynchronous function.

        This ensures that the 'handle' method is defined as a coroutine.

        Returns:
            None. The test passes if 'handle' is a coroutine function.
        """
        self.assertTrue(asyncio.iscoroutinefunction(CustomCommandComplete.handle))
