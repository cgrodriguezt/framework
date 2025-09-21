from orionis.foundation.config.logging.entities.chunked import Chunked
from orionis.foundation.config.logging.enums.levels import Level
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigLoggingChunked(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Verify that a Chunked instance is created with correct default values.

        This method ensures that a `Chunked` instance is created with the correct default values
        for `path`, `level`, `mb_size`, and `files`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Chunked instance with default parameters
        chunked = Chunked()

        # Assert that all default values are as expected
        self.assertEqual(chunked.path, "storage/logs/chunked.log")
        self.assertEqual(chunked.level, Level.INFO.value)
        self.assertEqual(chunked.mb_size, 10)
        self.assertEqual(chunked.files, 5)

    async def testPathValidation(self):
        """
        Validate the `path` attribute for correct type and value.

        This method verifies that empty or non-string paths raise `OrionisIntegrityException`.
        Also checks that a valid path does not raise an exception.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test empty string for path
        with self.assertRaises(OrionisIntegrityException):
            Chunked(path="")

        # Test non-string type for path
        with self.assertRaises(OrionisIntegrityException):
            Chunked(path=123)

        # Test valid path
        try:
            Chunked(path="custom/log/path.log")
        except OrionisIntegrityException:
            self.fail("Valid path should not raise exception")

    async def testLevelValidation(self):
        """
        Validate the `level` attribute for accepted types and error handling.

        This method checks that the `level` can be set using a string, integer, or enum,
        and that invalid values raise `OrionisIntegrityException`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test string value for level
        chunked = Chunked(level="debug")
        self.assertEqual(chunked.level, Level.DEBUG.value)

        # Test integer value for level
        chunked = Chunked(level=Level.WARNING.value)
        self.assertEqual(chunked.level, Level.WARNING.value)

        # Test enum value for level
        chunked = Chunked(level=Level.ERROR)
        self.assertEqual(chunked.level, Level.ERROR.value)

        # Test invalid string value for level
        with self.assertRaises(OrionisIntegrityException):
            Chunked(level="invalid")

        # Test invalid integer value for level
        with self.assertRaises(OrionisIntegrityException):
            Chunked(level=999)

        # Test invalid type for level
        with self.assertRaises(OrionisIntegrityException):
            Chunked(level=[])

    async def testMbSizeValidation(self):
        """
        Validate the `mb_size` attribute for accepted values and error handling.

        This method ensures that valid values for `mb_size` are accepted and invalid values raise
        OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test valid mb_size values
        chunked = Chunked(mb_size=10)
        self.assertEqual(chunked.mb_size, 10)

        chunked = Chunked(mb_size=1000)
        self.assertEqual(chunked.mb_size, 1000)

        # Test invalid mb_size value
        with self.assertRaises(OrionisIntegrityException):
            chunked = Chunked(mb_size=2048)
            self.assertEqual(chunked.mb_size, 2048)

    async def testFilesValidation(self):
        """
        Validate the `files` attribute for accepted values and error handling.

        This method ensures that valid integer values are accepted, and invalid values raise
        `OrionisIntegrityException`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test valid values for files
        try:
            Chunked(files=1)
            Chunked(files=10)
        except OrionisIntegrityException:
            self.fail("Valid files count should not raise exception")

        # Test invalid values for files
        with self.assertRaises(OrionisIntegrityException):
            Chunked(files=0)

        with self.assertRaises(OrionisIntegrityException):
            Chunked(files=-1)

        with self.assertRaises(OrionisIntegrityException):
            Chunked(files="5")

    async def testWhitespaceHandling(self):
        """
        Validate handling of whitespace in `path` and `level` attributes.

        This method ensures that values containing whitespace are handled as expected and
        that invalid whitespace usage raises OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Chunked with whitespace in path and level; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            chunked = Chunked(path="  logs/app.log  ", level="  debug  ")
            self.assertEqual(chunked.path, "  logs/app.log  ")
            self.assertEqual(chunked.level, Level.DEBUG.value)

    async def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Chunked.

        This method ensures that `toDict` returns a dictionary representation of the instance
        with correct values for all attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Chunked instance with default parameters
        chunked = Chunked()

        # Convert the Chunked instance to a dictionary
        chunked_dict = chunked.toDict()

        # Assert that the dictionary contains the correct values
        self.assertIsInstance(chunked_dict, dict)
        self.assertEqual(chunked_dict['path'], "storage/logs/chunked.log")
        self.assertEqual(chunked_dict['level'], Level.INFO.value)
        self.assertEqual(chunked_dict['mb_size'], 10)
        self.assertEqual(chunked_dict['files'], 5)

    async def testCustomValuesToDict(self):
        """
        Validate the dictionary output of toDict with custom values.

        This method ensures that custom values provided to the constructor are correctly
        reflected in the dictionary representation.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Chunked instance with custom values
        custom_chunked = Chunked(
            path="custom/logs/app.log",
            level="warning",
            mb_size=20,
            files=10
        )

        # Convert the custom Chunked instance to a dictionary
        chunked_dict = custom_chunked.toDict()

        # Assert that the dictionary contains the custom values
        self.assertEqual(chunked_dict['path'], "custom/logs/app.log")
        self.assertEqual(chunked_dict['level'], 30)
        self.assertEqual(chunked_dict['mb_size'], 20)
        self.assertEqual(chunked_dict['files'], 10)

    async def testHashability(self):
        """
        Validate hashability of Chunked instances.

        This method ensures that `Chunked` instances are hashable and can be used in sets,
        due to `unsafe_hash=True`, and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Chunked instances
        chunked1 = Chunked()
        chunked2 = Chunked()

        # Add both to a set; should only contain one unique instance
        chunked_set = {chunked1, chunked2}
        self.assertEqual(len(chunked_set), 1)

        # Add a custom Chunked instance with a different path
        custom_chunked = Chunked(path="custom.log")
        chunked_set.add(custom_chunked)

        # Now the set should contain two unique instances
        self.assertEqual(len(chunked_set), 2)

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Chunked.

        This method ensures that `Chunked` cannot be initialized with positional arguments,
        and raises a `TypeError` if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Chunked with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Chunked("path.log", "info", 10, 5)