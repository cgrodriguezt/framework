from datetime import time
from orionis.foundation.config.logging.entities.daily import Daily
from orionis.foundation.config.logging.enums.levels import Level
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigLoggingDaily(SyncTestCase):

    def testDefaultValues(self):
        """
        Verify that a Daily instance is created with correct default values.

        This method ensures that the default path, level, retention_days, and at time
        are set as expected in a Daily instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Daily instance with default parameters
        daily = Daily()

        # Assert that all default values are as expected
        self.assertEqual(daily.path, "storage/logs/daily.log")
        self.assertEqual(daily.level, Level.INFO.value)
        self.assertEqual(daily.retention_days, 7)
        self.assertEqual(daily.at, "00:00")

    def testPathValidation(self):
        """
        Validate the path attribute for correct type and value.

        This method verifies that empty or non-string paths raise exceptions, and that
        valid paths are accepted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test empty string for path
        with self.assertRaises(OrionisIntegrityException):
            Daily(path="")

        # Test non-string type for path
        with self.assertRaises(OrionisIntegrityException):
            Daily(path=123)

        # Test valid path
        try:
            Daily(path="custom/log/path.log")
        except OrionisIntegrityException:
            self.fail("Valid path should not raise exception")

    def testLevelValidation(self):
        """
        Validate the level attribute for accepted types and error handling.

        This method checks that string, integer, and enum values are accepted for level,
        and that invalid values raise exceptions.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test string value for level
        daily = Daily(level="debug")
        self.assertEqual(daily.level, Level.DEBUG.value)

        # Test integer value for level
        daily = Daily(level=Level.WARNING.value)
        self.assertEqual(daily.level, Level.WARNING.value)

        # Test enum value for level
        daily = Daily(level=Level.ERROR)
        self.assertEqual(daily.level, Level.ERROR.value)

        # Test invalid string value for level
        with self.assertRaises(OrionisIntegrityException):
            Daily(level="invalid")

        # Test invalid integer value for level
        with self.assertRaises(OrionisIntegrityException):
            Daily(level=999)

        # Test invalid type for level
        with self.assertRaises(OrionisIntegrityException):
            Daily(level=[])

    def testRetentionDaysValidation(self):
        """
        Validate the retention_days attribute for accepted values and error handling.

        This method ensures that valid values are accepted and invalid values raise exceptions.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test valid values for retention_days
        try:
            Daily(retention_days=1)
            Daily(retention_days=90)
            Daily(retention_days=30)
        except OrionisIntegrityException:
            self.fail("Valid retention_days should not raise exception")

        # Test invalid values for retention_days
        with self.assertRaises(OrionisIntegrityException):
            Daily(retention_days=0)

        with self.assertRaises(OrionisIntegrityException):
            Daily(retention_days=91)

        with self.assertRaises(OrionisIntegrityException):
            Daily(retention_days=-1)

        with self.assertRaises(OrionisIntegrityException):
            Daily(retention_days="7")

    def testAtTimeValidation(self):
        """
        Validate the at attribute for correct type and conversion.

        This method checks that a `datetime.time` object is properly converted and that
        invalid types raise exceptions.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test valid time object for at
        daily = Daily(at=time(12, 30))
        self.assertEqual(daily.at, "12:30")

        # Test invalid types for at
        with self.assertRaises(OrionisIntegrityException):
            Daily(at="12:00:00")

        with self.assertRaises(OrionisIntegrityException):
            Daily(at=1200)

    def testWhitespaceHandling(self):
        """
        Validate handling of whitespace in path and level attributes.

        This method ensures that values containing whitespace are handled as expected and
        that invalid whitespace usage raises OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Daily with whitespace in path and level; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Daily(path="  logs/app.log  ", level="  debug  ")

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Daily.

        This method ensures that the dictionary returned by toDict contains the correct
        default values for all attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Daily instance with default parameters
        daily = Daily()

        # Convert the Daily instance to a dictionary
        daily_dict = daily.toDict()

        # Assert that the dictionary contains the correct default values
        self.assertIsInstance(daily_dict, dict)
        self.assertEqual(daily_dict['path'], "storage/logs/daily.log")
        self.assertEqual(daily_dict['level'], Level.INFO.value)
        self.assertEqual(daily_dict['retention_days'], 7)
        self.assertEqual(daily_dict['at'], "00:00")

    def testCustomValuesToDict(self):
        """
        Validate the dictionary output of toDict with custom values.

        This method ensures that custom values are correctly represented in the dictionary
        returned by toDict.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Daily instance with custom values
        custom_daily = Daily(
            path="custom/logs/app.log",
            level="warning",
            retention_days=14,
            at=time(23, 59)
        )

        # Convert the custom Daily instance to a dictionary
        daily_dict = custom_daily.toDict()

        # Assert that the dictionary contains the custom values
        self.assertEqual(daily_dict['path'], "custom/logs/app.log")
        self.assertEqual(daily_dict['level'], Level.WARNING.value)
        self.assertEqual(daily_dict['retention_days'], 14)
        self.assertEqual(daily_dict['at'], "23:59")

    def testHashability(self):
        """
        Validate hashability of Daily instances.

        This method ensures that Daily instances are hashable and can be used in sets,
        and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Daily instances
        daily1 = Daily()
        daily2 = Daily()

        # Add both to a set; should only contain one unique instance
        daily_set = {daily1, daily2}
        self.assertEqual(len(daily_set), 1)

        # Add a custom Daily instance with a different path
        custom_daily = Daily(path="custom.log")
        daily_set.add(custom_daily)

        # Now the set should contain two unique instances
        self.assertEqual(len(daily_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Daily.

        This method ensures that positional arguments raise a TypeError when initializing Daily.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Daily with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Daily("path.log", "info", 7, time(0, 0))