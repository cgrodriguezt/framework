from orionis.foundation.config.logging.entities.channels import Channels
from orionis.foundation.config.logging.entities.stack import Stack
from orionis.foundation.config.logging.entities.hourly import Hourly
from orionis.foundation.config.logging.entities.daily import Daily
from orionis.foundation.config.logging.entities.weekly import Weekly
from orionis.foundation.config.logging.entities.monthly import Monthly
from orionis.foundation.config.logging.entities.chunked import Chunked
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigLoggingChannels(SyncTestCase):

    def testDefaultValues(self):
        """
        Verify that a Channels instance is initialized with correct default values.

        This method ensures that all channel configuration attributes are instances of their
        respective classes upon default initialization.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Channels instance with default parameters
        channels = Channels()

        # Assert that each channel attribute is an instance of the correct class
        self.assertIsInstance(channels.stack, Stack)
        self.assertIsInstance(channels.hourly, Hourly)
        self.assertIsInstance(channels.daily, Daily)
        self.assertIsInstance(channels.weekly, Weekly)
        self.assertIsInstance(channels.monthly, Monthly)
        self.assertIsInstance(channels.chunked, Chunked)

    def testStackValidation(self):
        """
        Validate that only Stack instances are accepted for the stack attribute.

        This method ensures that the stack attribute only accepts Stack instances and raises
        OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid types for the stack attribute
        with self.assertRaises(OrionisIntegrityException):
            Channels(stack="not_a_stack_instance")

        with self.assertRaises(OrionisIntegrityException):
            Channels(stack=123)

        # Test valid Stack instance
        try:
            Channels(stack=Stack())
        except OrionisIntegrityException:
            self.fail("Valid Stack instance should not raise exception")

    def testHourlyValidation(self):
        """
        Validate that only Hourly instances are accepted for the hourly attribute.

        This method ensures that the hourly attribute only accepts Hourly instances and raises
        OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid type for the hourly attribute
        with self.assertRaises(OrionisIntegrityException):
            Channels(hourly="not_an_hourly_instance")

        # Test valid Hourly instance
        try:
            Channels(hourly=Hourly())
        except OrionisIntegrityException:
            self.fail("Valid Hourly instance should not raise exception")

    def testDailyValidation(self):
        """
        Validate that only Daily instances are accepted for the daily attribute.

        This method ensures that the daily attribute only accepts Daily instances and raises
        OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid type for the daily attribute
        with self.assertRaises(OrionisIntegrityException):
            Channels(daily="not_a_daily_instance")

        # Test valid Daily instance
        try:
            Channels(daily=Daily())
        except OrionisIntegrityException:
            self.fail("Valid Daily instance should not raise exception")

    def testWeeklyValidation(self):
        """
        Validate that only Weekly instances are accepted for the weekly attribute.

        This method ensures that the weekly attribute only accepts Weekly instances and raises
        OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid type for the weekly attribute
        with self.assertRaises(OrionisIntegrityException):
            Channels(weekly="not_a_weekly_instance")

        # Test valid Weekly instance
        try:
            Channels(weekly=Weekly())
        except OrionisIntegrityException:
            self.fail("Valid Weekly instance should not raise exception")

    def testMonthlyValidation(self):
        """
        Validate that only Monthly instances are accepted for the monthly attribute.

        This method ensures that the monthly attribute only accepts Monthly instances and raises
        OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid type for the monthly attribute
        with self.assertRaises(OrionisIntegrityException):
            Channels(monthly="not_a_monthly_instance")

        # Test valid Monthly instance
        try:
            Channels(monthly=Monthly())
        except OrionisIntegrityException:
            self.fail("Valid Monthly instance should not raise exception")

    def testChunkedValidation(self):
        """
        Validate that only Chunked instances are accepted for the chunked attribute.

        This method ensures that the chunked attribute only accepts Chunked instances and raises
        OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid type for the chunked attribute
        with self.assertRaises(OrionisIntegrityException):
            Channels(chunked="not_a_chunked_instance")

        # Test valid Chunked instance
        try:
            Channels(chunked=Chunked())
        except OrionisIntegrityException:
            self.fail("Valid Chunked instance should not raise exception")

    def testCustomConfigurations(self):
        """
        Validate assignment and storage of custom channel configurations.

        This method ensures that custom channel instances are properly set and their properties
        are accurately assigned in the Channels instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create custom channel configuration instances
        custom_stack = Stack(path="custom/stack.log")
        custom_hourly = Hourly(path="custom/hourly.log")
        custom_daily = Daily(path="custom/daily.log")
        custom_weekly = Weekly(path="custom/weekly.log")
        custom_monthly = Monthly(path="custom/monthly.log")
        custom_chunked = Chunked(path="custom/chunked.log")

        # Create a Channels instance with custom configurations
        channels = Channels(
            stack=custom_stack,
            hourly=custom_hourly,
            daily=custom_daily,
            weekly=custom_weekly,
            monthly=custom_monthly,
            chunked=custom_chunked
        )

        # Assert that all custom values are correctly assigned
        self.assertEqual(channels.stack.path, "custom/stack.log")
        self.assertEqual(channels.hourly.path, "custom/hourly.log")
        self.assertEqual(channels.daily.path, "custom/daily.log")
        self.assertEqual(channels.weekly.path, "custom/weekly.log")
        self.assertEqual(channels.monthly.path, "custom/monthly.log")
        self.assertEqual(channels.chunked.path, "custom/chunked.log")

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Channels.

        This method ensures that the `toDict` method produces a dictionary with the expected
        structure and types for each channel.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Channels instance with default parameters
        channels = Channels()

        # Convert the Channels instance to a dictionary
        channels_dict = channels.toDict()

        # Assert that the dictionary contains the correct structure and types
        self.assertIsInstance(channels_dict, dict)
        self.assertIsInstance(channels_dict['stack'], dict)
        self.assertIsInstance(channels_dict['hourly'], dict)
        self.assertIsInstance(channels_dict['daily'], dict)
        self.assertIsInstance(channels_dict['weekly'], dict)
        self.assertIsInstance(channels_dict['monthly'], dict)
        self.assertIsInstance(channels_dict['chunked'], dict)

    def testHashability(self):
        """
        Validate hashability of Channels instances.

        This method ensures that Channels objects can be used in sets and as dictionary keys
        due to unsafe_hash=True, and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Channels instances
        channels1 = Channels()
        channels2 = Channels()

        # Add both to a set; should only contain one unique instance
        channels_set = {channels1, channels2}
        self.assertEqual(len(channels_set), 1)

        # Add a custom Channels instance with a different stack path
        custom_channels = Channels(stack=Stack(path="custom.log"))
        channels_set.add(custom_channels)

        # Now the set should contain two unique instances
        self.assertEqual(len(channels_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Channels.

        This method ensures that Channels enforces keyword-only arguments and does not
        allow positional arguments during initialization. Raises TypeError if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Channels with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Channels(Stack(), Hourly(), Daily(), Weekly(), Monthly(), Chunked())