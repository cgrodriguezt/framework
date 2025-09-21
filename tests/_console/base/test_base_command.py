import asyncio
from orionis.console.base.command import BaseCommand
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.base.mock.mock_command import CustomCommandWithoutHandle, CustomCommandComplete

class TestBaseCommand(AsyncTestCase):

    async def testHandleNotImplemented(self):
        """
        Tests that calling 'handle' on a command without an implementation raises NotImplementedError.

        This test instantiates a command class that does not override 'handle' and asserts
        that calling or awaiting 'handle' raises NotImplementedError.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if NotImplementedError is raised.
        """
        command = CustomCommandWithoutHandle()
        with self.assertRaises(NotImplementedError):
            if asyncio.iscoroutinefunction(command.handle):
                await command.handle()
            else:
                command.handle()

    async def testHandleAsyncSuccess(self):
        """
        Tests successful execution of the async 'handle' method in CustomCommandComplete.

        This test creates an instance of CustomCommandComplete and awaits its 'handle' method,
        asserting that the returned value matches the expected result.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if the result is as expected.
        """
        command = CustomCommandComplete()
        result = await command.handle()
        self.assertEqual(result, "Finished Successfully")

    async def testIsSubclassOfBaseCommand(self):
        """
        Checks that CustomCommandComplete and CustomCommandWithoutHandle inherit from BaseCommand.

        This test asserts that both mock command classes are direct subclasses of BaseCommand.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if both classes inherit from BaseCommand.
        """
        self.assertIn(BaseCommand, CustomCommandComplete.__bases__)
        self.assertIn(BaseCommand, CustomCommandWithoutHandle.__bases__)

    async def testArgsProperty(self):
        """
        Verifies that the 'args' property returns the expected dictionary of arguments.

        This test checks that the 'args' property of both mock command classes matches
        the predefined dictionary of expected argument values.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if the 'args' property matches the expected dictionary.
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
        self.assertEqual(command.args, expected_args)
        command2 = CustomCommandWithoutHandle()
        self.assertEqual(command2.args, expected_args)

    async def testArgsTypes(self):
        """
        Validates the types of values in the 'args' property of CustomCommandComplete.

        This test checks that each key in the 'args' dictionary corresponds to a value of the expected type.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if all argument types match their expected Python types.
        """
        command = CustomCommandComplete()
        args = command.args
        self.assertIsInstance(args['key_str'], str)
        self.assertIsInstance(args['key_int'], int)
        self.assertIsInstance(args['key_float'], float)
        self.assertIsInstance(args['key_bool'], bool)
        self.assertIsInstance(args['key_list'], list)
        self.assertIsInstance(args['key_dict'], dict)

    async def testHandleIsAsync(self):
        """
        Checks whether the 'handle' method of CustomCommandComplete is asynchronous.

        This test asserts that the 'handle' method is a coroutine function.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if 'handle' is a coroutine function.
        """
        self.assertTrue(asyncio.iscoroutinefunction(CustomCommandComplete.handle))

    async def testArgumentMethodReturnsCorrectValue(self):
        """
        Tests the 'argument' method returns the correct value for a given key.

        This test sets the _args attribute and checks that the 'argument' method
        retrieves the correct value for a valid key.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if the correct value is returned.
        """
        class DummyCommand(BaseCommand):
            signature = "dummy"
            description = "dummy"
            _args = {'foo': 'bar'}
            async def handle(self):
                return None
        command = DummyCommand()
        self.assertEqual(command.argument('foo'), 'bar')

    async def testArgumentMethodReturnsDefault(self):
        """
        Tests the 'argument' method returns the default value if key is missing.

        This test checks that the 'argument' method returns the provided default
        when the key is not present in _args.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if the default value is returned.
        """
        class DummyCommand(BaseCommand):
            signature = "dummy"
            description = "dummy"
            _args = {}
            async def handle(self):
                return None
        command = DummyCommand()
        self.assertEqual(command.argument('missing', default='default_value'), 'default_value')

    async def testArgumentMethodTypeValidation(self):
        """
        Tests that the 'argument' method raises ValueError for invalid key type or _args type.

        This test checks that a ValueError is raised if the key is not a string or if _args is not a dict.

        Parameters
        ----------
        self : TestBaseCommand
            The test case instance.

        Returns
        -------
        None
            Passes if ValueError is raised for invalid input.
        """
        class DummyCommand(BaseCommand):
            signature = "dummy"
            description = "dummy"
            _args = {'foo': 'bar'}
            async def handle(self):
                return None
        command = DummyCommand()
        with self.assertRaises(ValueError):
            command.argument(123)
        command._args = []
        with self.assertRaises(ValueError):
            command.argument('foo')
