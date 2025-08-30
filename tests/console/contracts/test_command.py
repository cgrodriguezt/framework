from orionis.test.cases.asynchronous import AsyncTestCase
from tests.console.contracts.dummy.dummy_command import DummyCommandTwo

class TestICommand(AsyncTestCase):

    async def testTimestampDefault(self):
        """
        Enables or disables the timestamp for the command.

        When called without arguments, the timestamp is enabled by default.
        This method is used to control whether the command output includes a timestamp.

        Returns
        -------
        DummyCommandTwo
            The command instance with the updated timestamp setting.
        """
        # Create a new DummyCommandTwo instance
        cmd = DummyCommandTwo()
        # Call timestamp() with default argument (should enable timestamp)
        result = cmd.timestamp()
        # Assert that timestamp is enabled by default
        assert result._timestamp_enabled is True

    async def testTimestampFalse(self):
        """
        Enables or disables the timestamp for the command.

        Passing False as an argument disables the timestamp.
        This method is used to control whether the command output includes a timestamp.

        Returns
        -------
        DummyCommandTwo
            The command instance with the updated timestamp setting.
        """
        # Create a new DummyCommandTwo instance
        cmd = DummyCommandTwo()
        # Call timestamp() with False to disable timestamp
        result = cmd.timestamp(False)
        # Assert that timestamp is disabled
        assert result._timestamp_enabled is False

    async def testTimestampTypeError(self):
        """
        Raises a TypeError if a non-boolean value is provided for the timestamp argument.

        Ensures that only boolean values are accepted for enabling or disabling the timestamp.

        Returns
        -------
        None
            This method does not return a value. It asserts that a TypeError is raised.
        """
        # Create a new DummyCommandTwo instance
        cmd = DummyCommandTwo()
        try:
            # Attempt to pass a non-boolean value to timestamp()
            cmd.timestamp("yes")
            assert False, "TypeError not raised"
        except TypeError:
            # Expected outcome: TypeError is raised
            pass

    async def testDescriptionValid(self):
        """
        Sets the description for the command.

        Accepts a string value and assigns it as the command's description.

        Returns
        -------
        DummyCommandTwo
            The command instance with the updated description.
        """
        # Create a new DummyCommandTwo instance
        cmd = DummyCommandTwo()
        desc = "This is a test command."
        # Set the description using a valid string
        result = cmd.description(desc)
        # Assert that the description is set correctly
        assert result._description == desc

    async def testDescriptionTypeError(self):
        """
        Raises a TypeError if a non-string value is provided for the description.

        Ensures that only string values are accepted as the command's description.

        Returns
        -------
        None
            This method does not return a value. It asserts that a TypeError is raised.
        """
        # Create a new DummyCommandTwo instance
        cmd = DummyCommandTwo()
        try:
            # Attempt to set description with a non-string value
            cmd.description(123)
            assert False, "TypeError not raised"
        except TypeError:
            # Expected outcome: TypeError is raised
            pass

    async def testArgumentsValid(self):
        """
        Sets the arguments for the command.

        Accepts a list of arguments and assigns them to the command.

        Returns
        -------
        DummyCommandTwo
            The command instance with the updated arguments.
        """
        # Create a new DummyCommandTwo instance
        cmd = DummyCommandTwo()
        args = ["arg1", "arg2"]
        # Set the arguments using a valid list
        result = cmd.arguments(args)
        # Assert that the arguments are set correctly
        assert result._arguments == args

    async def testArgumentsTypeError(self):
        """
        Raises a TypeError if a non-list value is provided for the arguments.

        Ensures that only list values are accepted as the command's arguments.

        Returns
        -------
        None
            This method does not return a value. It asserts that a TypeError is raised.
        """
        # Create a new DummyCommandTwo instance
        cmd = DummyCommandTwo()
        try:
            # Attempt to set arguments with a non-list value
            cmd.arguments("notalist")
            assert False, "TypeError not raised"
        except TypeError:
            # Expected outcome: TypeError is raised
            pass
