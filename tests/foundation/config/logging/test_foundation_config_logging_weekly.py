from orionis.foundation.config.logging.entities.weekly import Weekly
from orionis.foundation.config.logging.enums.levels import Level
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigLoggingWeekly(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Verify that a Weekly instance is created with correct default values.

        This method checks that the default `path`, `level`, and `retention_weeks` attributes
        of a `Weekly` instance match the expected values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Weekly instance with default parameters
        weekly = Weekly()

        # Assert that the default path, level, and retention_weeks are as expected
        self.assertEqual(weekly.path, "storage/log/weekly.log")
        self.assertEqual(weekly.level, Level.INFO.value)
        self.assertEqual(weekly.retention_weeks, 4)

    async def testPathValidation(self):
        """
        Validate the path attribute for correct type and value.

        This method verifies that empty or non-string `path` values raise exceptions,
        and that a valid path does not raise an exception.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test empty string for path
        with self.assertRaises(OrionisIntegrityException):
            Weekly(path="")

        # Test non-string type for path
        with self.assertRaises(OrionisIntegrityException):
            Weekly(path=123)

        # Test valid path
        try:
            Weekly(path="custom/log/path.log")
        except OrionisIntegrityException:
            self.fail("Valid path should not raise exception")

    async def testLevelValidation(self):
        """
        Validate the level attribute for accepted types and error handling.

        This method checks that the `level` attribute accepts string, integer, and enum values,
        and raises exceptions for invalid types or values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test string value for level
        weekly = Weekly(level="debug")
        self.assertEqual(weekly.level, Level.DEBUG.value)

        # Test integer value for level
        weekly = Weekly(level=Level.WARNING.value)
        self.assertEqual(weekly.level, Level.WARNING.value)

        # Test enum value for level
        weekly = Weekly(level=Level.ERROR)
        self.assertEqual(weekly.level, Level.ERROR.value)

        # Test invalid string value for level
        with self.assertRaises(OrionisIntegrityException):
            Weekly(level="invalid")

        # Test invalid integer value for level
        with self.assertRaises(OrionisIntegrityException):
            Weekly(level=999)

        # Test invalid type for level
        with self.assertRaises(OrionisIntegrityException):
            Weekly(level=[])

    async def testRetentionWeeksValidation(self):
        """
        Validate the retention_weeks attribute for correct values and error handling.

        This method ensures that valid `retention_weeks` values are accepted and invalid
        values raise exceptions.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test valid values for retention_weeks
        try:
            Weekly(retention_weeks=1)
            Weekly(retention_weeks=12)
            Weekly(retention_weeks=6)
        except OrionisIntegrityException:
            self.fail("Valid retention_weeks should not raise exception")

        # Test invalid values for retention_weeks
        with self.assertRaises(OrionisIntegrityException):
            Weekly(retention_weeks=0)
        with self.assertRaises(OrionisIntegrityException):
            Weekly(retention_weeks=13)
        with self.assertRaises(OrionisIntegrityException):
            Weekly(retention_weeks=-1)
        with self.assertRaises(OrionisIntegrityException):
            Weekly(retention_weeks="4")

    async def testWhitespaceHandling(self):
        """
        Validate handling of whitespace in path and level attributes.

        This method verifies that leading and trailing whitespace in `path` and `level`
        attributes are handled as expected and raise exceptions if not valid.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Weekly with whitespace in path and level; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            weekly = Weekly(path="  logs/app.log  ", level="  debug  ")
            self.assertEqual(weekly.path, "  logs/app.log  ")
            self.assertEqual(weekly.level, Level.DEBUG.value)

    async def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Weekly.

        This method ensures that the `toDict` method returns a dictionary with the correct
        keys and values for a default `Weekly` instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Weekly instance with default parameters
        weekly = Weekly()

        # Convert the Weekly instance to a dictionary
        weekly_dict = weekly.toDict()

        # Assert that the dictionary contains the correct values
        self.assertIsInstance(weekly_dict, dict)
        self.assertEqual(weekly_dict['path'], "storage/log/weekly.log")
        self.assertEqual(weekly_dict['level'], Level.INFO.value)
        self.assertEqual(weekly_dict['retention_weeks'], 4)

    async def testCustomValuesToDict(self):
        """
        Validate the dictionary output of toDict with custom values.

        This method checks that custom attribute values are correctly represented in the
        dictionary returned by `toDict`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Weekly instance with custom values
        custom_weekly = Weekly(
            path="custom/logs/app.log",
            level="warning",
            retention_weeks=8
        )

        # Convert the custom Weekly instance to a dictionary
        weekly_dict = custom_weekly.toDict()

        # Assert that the dictionary contains the custom values
        self.assertEqual(weekly_dict['path'], "custom/logs/app.log")
        self.assertEqual(weekly_dict['level'], Level.WARNING.value)
        self.assertEqual(weekly_dict['retention_weeks'], 8)

    async def testHashability(self):
        """
        Validate hashability of Weekly instances.

        This method verifies that `Weekly` instances are hashable and can be used in sets,
        and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Weekly instances
        weekly1 = Weekly()
        weekly2 = Weekly()

        # Add both to a set; should only contain one unique instance
        weekly_set = {weekly1, weekly2}
        self.assertEqual(len(weekly_set), 1)

        # Add a custom Weekly instance with a different path
        custom_weekly = Weekly(path="custom.log")
        weekly_set.add(custom_weekly)

        # Now the set should contain two unique instances
        self.assertEqual(len(weekly_set), 2)

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Weekly.

        This method ensures that providing positional arguments to the `Weekly` constructor
        raises a TypeError.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Weekly with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Weekly("path.log", "info", 4)