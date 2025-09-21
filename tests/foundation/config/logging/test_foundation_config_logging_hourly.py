from orionis.foundation.config.logging.entities.hourly import Hourly
from orionis.foundation.config.logging.enums.levels import Level
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigLoggingHourly(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Verify that an Hourly instance is created with correct default values.

        This method ensures that the default `path`, `level`, and `retention_hours` attributes
        of the Hourly instance match the expected values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create an Hourly instance with default parameters
        hourly = Hourly()

        # Assert that all default values are as expected
        self.assertEqual(hourly.path, "storage/logs/hourly.log")
        self.assertEqual(hourly.level, Level.INFO.value)
        self.assertEqual(hourly.retention_hours, 24)

    async def testPathValidation(self):
        """
        Validate the path attribute for correct type and value.

        This method ensures that invalid values for the `path` attribute, such as empty strings
        or non-string types, raise an `OrionisIntegrityException`. Also verifies that
        valid paths do not raise exceptions.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test empty string for path
        with self.assertRaises(OrionisIntegrityException):
            Hourly(path="")

        # Test non-string type for path
        with self.assertRaises(OrionisIntegrityException):
            Hourly(path=123)

        # Test valid path
        try:
            Hourly(path="custom/log/path.log")
        except OrionisIntegrityException:
            self.fail("Valid path should not raise exception")

    async def testLevelValidation(self):
        """
        Validate the level attribute for accepted types and error handling.

        This method checks that the `level` attribute accepts string, integer, and enum values,
        and that invalid values raise an `OrionisIntegrityException`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test string value for level
        hourly = Hourly(level="debug")
        self.assertEqual(hourly.level, Level.DEBUG.value)

        # Test integer value for level
        hourly = Hourly(level=Level.WARNING.value)
        self.assertEqual(hourly.level, Level.WARNING.value)

        # Test enum value for level
        hourly = Hourly(level=Level.ERROR)
        self.assertEqual(hourly.level, Level.ERROR.value)

        # Test invalid string value for level
        with self.assertRaises(OrionisIntegrityException):
            Hourly(level="invalid")

        # Test invalid integer value for level
        with self.assertRaises(OrionisIntegrityException):
            Hourly(level=999)

        # Test invalid type for level
        with self.assertRaises(OrionisIntegrityException):
            Hourly(level=[])

    async def testRetentionHoursValidation(self):
        """
        Validate the retention_hours attribute for accepted values and error handling.

        This method ensures that valid values for `retention_hours` are accepted and invalid
        values raise an `OrionisIntegrityException`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test valid values for retention_hours
        try:
            Hourly(retention_hours=1)
            Hourly(retention_hours=168)
            Hourly(retention_hours=72)
        except OrionisIntegrityException:
            self.fail("Valid retention_hours should not raise exception")

        # Test invalid values for retention_hours
        with self.assertRaises(OrionisIntegrityException):
            Hourly(retention_hours=0)

        with self.assertRaises(OrionisIntegrityException):
            Hourly(retention_hours=169)

        with self.assertRaises(OrionisIntegrityException):
            Hourly(retention_hours=-1)

        with self.assertRaises(OrionisIntegrityException):
            Hourly(retention_hours="24")

    async def testWhitespaceHandling(self):
        """
        Validate handling of whitespace in path and level attributes.

        This method ensures that values containing whitespace are handled as expected and
        that invalid whitespace usage raises OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Hourly with whitespace in path and level; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            hourly = Hourly(path="  logs/app.log  ", level="  debug  ")
            self.assertEqual(hourly.path, "  logs/app.log  ")
            self.assertEqual(hourly.level, Level.DEBUG.value)

    async def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Hourly.

        This method ensures that the `toDict` method returns a dictionary with the correct
        attribute values for all fields.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create an Hourly instance with default parameters
        hourly = Hourly()

        # Convert the Hourly instance to a dictionary
        hourly_dict = hourly.toDict()

        # Assert that the dictionary contains the correct values
        self.assertIsInstance(hourly_dict, dict)
        self.assertEqual(hourly_dict['path'], "storage/logs/hourly.log")
        self.assertEqual(hourly_dict['level'], Level.INFO.value)
        self.assertEqual(hourly_dict['retention_hours'], 24)

    async def testCustomValuesToDict(self):
        """
        Validate the dictionary output of toDict with custom values.

        This method ensures that custom values provided to the Hourly instance are correctly
        reflected in the dictionary returned by `toDict`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create an Hourly instance with custom values
        custom_hourly = Hourly(
            path="custom/logs/app.log",
            level="warning",
            retention_hours=48
        )

        # Convert the custom Hourly instance to a dictionary
        hourly_dict = custom_hourly.toDict()

        # Assert that the dictionary contains the custom values
        self.assertEqual(hourly_dict['path'], "custom/logs/app.log")
        self.assertEqual(hourly_dict['level'], Level.WARNING.value)
        self.assertEqual(hourly_dict['retention_hours'], 48)

    async def testHashability(self):
        """
        Validate hashability of Hourly instances.

        This method ensures that Hourly instances can be added to a set and that their
        hashability is preserved, and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Hourly instances
        hourly1 = Hourly()
        hourly2 = Hourly()

        # Add both to a set; should only contain one unique instance
        hourly_set = {hourly1, hourly2}
        self.assertEqual(len(hourly_set), 1)

        # Add a custom Hourly instance with a different path
        custom_hourly = Hourly(path="custom.log")
        hourly_set.add(custom_hourly)

        # Now the set should contain two unique instances
        self.assertEqual(len(hourly_set), 2)

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Hourly.

        This method ensures that attempting to initialize Hourly with positional arguments
        raises a TypeError.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Hourly with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Hourly("path.log", "info", 24)