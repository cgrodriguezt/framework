from orionis.foundation.config.logging.entities.stack import Stack
from orionis.foundation.config.logging.enums.levels import Level
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigLoggingStack(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Verify that a Stack instance is created with correct default values.

        This method checks that the default path and level attributes of a Stack instance
        match the expected class defaults.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Stack instance with default parameters
        stack = Stack()

        # Assert that the default path and level are as expected
        self.assertEqual(stack.path, "storage/logs/stack.log")
        self.assertEqual(stack.level, Level.INFO.value)

    async def testPathValidation(self):
        """
        Validate the path attribute for correct type and value.

        This method ensures that providing an empty string or a non-string value for the path
        raises an OrionisIntegrityException, while a valid string path is accepted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test empty string for path
        with self.assertRaises(OrionisIntegrityException):
            Stack(path="")

        # Test non-string type for path
        with self.assertRaises(OrionisIntegrityException):
            Stack(path=123)

        # Test valid path
        try:
            Stack(path="custom/log/path.log")
        except OrionisIntegrityException:
            self.fail("Valid path should not raise exception")

    async def testLevelValidation(self):
        """
        Validate the level attribute for accepted types and error handling.

        This method verifies that the level attribute accepts string, integer, and enum values
        corresponding to valid logging levels, and raises exceptions for invalid values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test string value for level
        stack = Stack(level="debug")
        self.assertEqual(stack.level, Level.DEBUG.value)

        # Test integer value for level
        stack = Stack(level=Level.WARNING.value)
        self.assertEqual(stack.level, Level.WARNING.value)

        # Test enum value for level
        stack = Stack(level=Level.ERROR)
        self.assertEqual(stack.level, Level.ERROR.value)

        # Test invalid string value for level
        with self.assertRaises(OrionisIntegrityException):
            Stack(level="invalid")

        # Test invalid integer value for level
        with self.assertRaises(OrionisIntegrityException):
            Stack(level=999)

        # Test invalid type for level
        with self.assertRaises(OrionisIntegrityException):
            Stack(level=[])

    async def testWhitespaceHandling(self):
        """
        Validate handling of whitespace in path and level attributes.

        This method ensures that leading or trailing whitespace in the path attribute is not accepted
        and raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Stack with whitespace in path; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            spaced_path = "  logs/app.log  "
            stack = Stack(path=spaced_path)
            self.assertEqual(stack.path, spaced_path)

    async def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Stack.

        This method verifies that the dictionary returned by toDict contains the correct path and
        level values for a Stack instance with default attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Stack instance with default parameters
        stack = Stack()

        # Convert the Stack instance to a dictionary
        stack_dict = stack.toDict()

        # Assert that the dictionary contains the correct values
        self.assertIsInstance(stack_dict, dict)
        self.assertEqual(stack_dict['path'], "storage/logs/stack.log")
        self.assertEqual(stack_dict['level'], Level.INFO.value)

    async def testCustomValuesToDict(self):
        """
        Validate the dictionary output of toDict with custom values.

        This method ensures that custom path and level values are accurately reflected in the
        dictionary returned by toDict.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Stack instance with custom values
        custom_stack = Stack(
            path="custom/logs/app.log",
            level="warning"
        )

        # Convert the custom Stack instance to a dictionary
        stack_dict = custom_stack.toDict()

        # Assert that the dictionary contains the custom values
        self.assertEqual(stack_dict['path'], "custom/logs/app.log")
        self.assertEqual(stack_dict['level'], Level.WARNING.value)

    async def testHashability(self):
        """
        Validate hashability of Stack instances.

        This method ensures that Stack instances can be added to sets and used as dictionary keys,
        and that instances with identical attributes are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Stack instances
        stack1 = Stack()
        stack2 = Stack()

        # Add both to a set; should only contain one unique instance
        stack_set = {stack1, stack2}
        self.assertEqual(len(stack_set), 1)

        # Add a custom Stack instance with a different path
        custom_stack = Stack(path="custom.log")
        stack_set.add(custom_stack)

        # Now the set should contain two unique instances
        self.assertEqual(len(stack_set), 2)

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Stack.

        This method ensures that attempting to initialize Stack with positional arguments raises
        a TypeError.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Stack with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Stack("path.log", "info")