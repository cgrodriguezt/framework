from orionis.foundation.config.logging.entities.monthly import Monthly
from orionis.foundation.config.logging.enums.levels import Level
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigLoggingMonthly(SyncTestCase):

    def testDefaultValues(self):
        """
        Verify that a Monthly instance is created with correct default values.

        This method ensures that the default path, level, and retention_months attributes
        of the Monthly instance match the expected values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Monthly instance with default parameters
        monthly = Monthly()

        # Assert that all default values are as expected
        self.assertEqual(monthly.path, "storage/logs/monthly.log")
        self.assertEqual(monthly.level, Level.INFO.value)
        self.assertEqual(monthly.retention_months, 4)

    def testPathValidation(self):
        """
        Validate the path attribute for correct type and value.

        This method ensures that empty or non-string paths raise OrionisIntegrityException,
        and that valid string paths are accepted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test empty string for path
        with self.assertRaises(OrionisIntegrityException):
            Monthly(path="")

        # Test non-string type for path
        with self.assertRaises(OrionisIntegrityException):
            Monthly(path=123)

        # Test valid path
        try:
            Monthly(path="custom/log/path.log")
        except OrionisIntegrityException:
            self.fail("Valid path should not raise exception")

    def testLevelValidation(self):
        """
        Validate the level attribute for accepted types and error handling.

        This method ensures that string, int, and enum values are accepted for level,
        and that invalid values raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test string value for level
        monthly = Monthly(level="debug")
        self.assertEqual(monthly.level, Level.DEBUG.value)

        # Test integer value for level
        monthly = Monthly(level=Level.WARNING.value)
        self.assertEqual(monthly.level, Level.WARNING.value)

        # Test enum value for level
        monthly = Monthly(level=Level.ERROR)
        self.assertEqual(monthly.level, Level.ERROR.value)

        # Test invalid string value for level
        with self.assertRaises(OrionisIntegrityException):
            Monthly(level="invalid")

        # Test invalid integer value for level
        with self.assertRaises(OrionisIntegrityException):
            Monthly(level=999)

        # Test invalid type for level
        with self.assertRaises(OrionisIntegrityException):
            Monthly(level=[])

    def testRetentionMonthsValidation(self):
        """
        Validate the retention_months attribute for accepted values and error handling.

        This method ensures that valid integer values for retention_months are accepted,
        and that invalid values raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test valid values for retention_months
        try:
            Monthly(retention_months=1)
            Monthly(retention_months=12)
            Monthly(retention_months=6)
        except OrionisIntegrityException:
            self.fail("Valid retention_months should not raise exception")

        # Test invalid values for retention_months
        with self.assertRaises(OrionisIntegrityException):
            Monthly(retention_months=0)

        with self.assertRaises(OrionisIntegrityException):
            Monthly(retention_months=13)

        with self.assertRaises(OrionisIntegrityException):
            Monthly(retention_months=-1)

        with self.assertRaises(OrionisIntegrityException):
            Monthly(retention_months="4")

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
        # Attempt to initialize Monthly with whitespace in path and level; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Monthly(path="  logs/app.log  ", level="  debug  ")

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Monthly.

        This method ensures that the output is a dictionary with correct keys and values
        for all attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Monthly instance with default parameters
        monthly = Monthly()

        # Convert the Monthly instance to a dictionary
        monthly_dict = monthly.toDict()

        # Assert that the dictionary contains the correct values
        self.assertIsInstance(monthly_dict, dict)
        self.assertEqual(monthly_dict["path"], "storage/logs/monthly.log")
        self.assertEqual(monthly_dict["level"], Level.INFO.value)
        self.assertEqual(monthly_dict["retention_months"], 4)

    def testCustomValuesToDict(self):
        """
        Validate the dictionary output of toDict with custom values.

        This method ensures that custom attribute values are reflected in the dictionary output.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Monthly instance with custom values
        custom_monthly = Monthly(
            path="custom/logs/app.log",
            level="warning",
            retention_months=6,
        )

        # Convert the custom Monthly instance to a dictionary
        monthly_dict = custom_monthly.toDict()

        # Assert that the dictionary contains the custom values
        self.assertEqual(monthly_dict["path"], "custom/logs/app.log")
        self.assertEqual(monthly_dict["level"], Level.WARNING.value)
        self.assertEqual(monthly_dict["retention_months"], 6)

    def testHashability(self):
        """
        Validate hashability of Monthly instances.

        This method ensures that Monthly instances are hashable and can be used in sets,
        and that identical instances are considered equal while different ones are distinct.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create two identical Monthly instances
        monthly1 = Monthly()
        monthly2 = Monthly()

        # Add both to a set; should only contain one unique instance
        monthly_set = {monthly1, monthly2}
        self.assertEqual(len(monthly_set), 1)

        # Add a custom Monthly instance with a different path
        custom_monthly = Monthly(path="custom.log")
        monthly_set.add(custom_monthly)

        # Now the set should contain two unique instances
        self.assertEqual(len(monthly_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Monthly.

        This method ensures that Monthly enforces keyword-only arguments and does not
        allow positional arguments during initialization. Raises TypeError if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Monthly with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Monthly("path.log", "info", 4)
