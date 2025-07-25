from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.base.mock_command import CustomCommandWithoutHandle, CustomCommandComplete

class TestBinding(AsyncTestCase):

    async def testCommandHandle(self):
        """
        Test the handle method of BaseCommand.

        This test verifies that the handle method raises NotImplementedError
        when called on an instance of BaseCommand, as it is an abstract method
        that must be implemented by subclasses.
        """

        # Test that handle raises NotImplementedError for incomplete command
        with self.assertRaises(NotImplementedError):
            command = CustomCommandWithoutHandle()
            command.handle()

        # Test that handle executes successfully for complete command
        command = CustomCommandComplete()
        result = await command.handle()
        self.assertEqual(result, "Finished Successfully")