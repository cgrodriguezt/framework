from orionis.test import TestCase
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.logging.entities.channels import Channels
from orionis.foundation.config.logging.entities.stack import Stack
from orionis.foundation.config.logging.entities.daily import Daily
from orionis.foundation.config.logging.enums.levels import Level

# ===========================================================================
# Level enum
# ===========================================================================

class TestLevelEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that all expected Level members are present.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            self.assertIn(name, Level._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the integer values assigned to each Level member.

        Returns
        -------
        None
            This method does not return a value.
        """
        import logging
        self.assertEqual(Level.DEBUG.value, logging.DEBUG)
        self.assertEqual(Level.INFO.value, logging.INFO)
        self.assertEqual(Level.WARNING.value, logging.WARNING)
        self.assertEqual(Level.ERROR.value, logging.ERROR)
        self.assertEqual(Level.CRITICAL.value, logging.CRITICAL)

    def testLookupByName(self) -> None:
        """
        Test that Level members can be retrieved by their name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Level["DEBUG"], Level.DEBUG)

    def testLookupByValue(self) -> None:
        """
        Test that Level members can be retrieved by their integer value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Level(20), Level.INFO)

    def testMemberCount(self) -> None:
        """
        Test that exactly five Level members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Level), 5)

    def testValuesAreIntegers(self) -> None:
        """
        Test that all Level values are integers.

        Returns
        -------
        None
            This method does not return a value.
        """
        for member in Level:
            self.assertIsInstance(member.value, int)

    def testIsHashable(self) -> None:
        """
        Test that Level members are hashable and usable as dict keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        mapping = {Level.ERROR: "error"}
        self.assertEqual(mapping[Level.ERROR], "error")

# ===========================================================================
# Stack entity
# ===========================================================================

class TestStackEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Stack can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Stack()
        self.assertIsInstance(s, Stack)

    def testDefaultPath(self) -> None:
        """
        Test that the default path is the standard log file location.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Stack()
        self.assertEqual(s.path, "storage/logs/stack.log")

    def testDefaultLevelIsNormalized(self) -> None:
        """
        Test that the default level is a valid Level integer value.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Stack()
        self.assertIn(s.level, [l.value for l in Level])

    def testCustomLevelIntAccepted(self) -> None:
        """
        Test that a valid integer level is accepted.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Stack(level=Level.ERROR.value)
        self.assertEqual(s.level, Level.ERROR.value)

    def testInvalidLevelRaisesError(self) -> None:
        """
        Test that an invalid level value raises ValueError or TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises((ValueError, TypeError)):
            Stack(level=99999)

    def testEmptyPathRaisesValueError(self) -> None:
        """
        Test that an empty path raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Stack(path="")

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Stack instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        s = Stack()
        with self.assertRaises(FrozenInstanceError):
            s.path = "other.log"  # type: ignore[misc]

# ===========================================================================
# Daily entity
# ===========================================================================

class TestDailyEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Daily can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        d = Daily()
        self.assertIsInstance(d, Daily)

    def testDefaultPath(self) -> None:
        """
        Test that the default daily log path contains the expected base name.

        Returns
        -------
        None
            This method does not return a value.
        """
        d = Daily()
        self.assertIn("daily", d.path)

    def testDefaultRetentionDays(self) -> None:
        """
        Test that the default retention_days is 7.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Daily().retention_days, 7)

    def testDefaultLevelIsNormalized(self) -> None:
        """
        Test that the default level is a valid Level integer value.

        Returns
        -------
        None
            This method does not return a value.
        """
        d = Daily()
        self.assertIn(d.level, [l.value for l in Level])

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Daily instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        d = Daily()
        with self.assertRaises(FrozenInstanceError):
            d.retention_days = 14  # type: ignore[misc]

# ===========================================================================
# Channels entity
# ===========================================================================

class TestChannelsEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Channels can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Channels()
        self.assertIsInstance(c, Channels)

    def testDefaultStackIsStackInstance(self) -> None:
        """
        Test that the default stack attribute is a Stack instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Channels().stack, Stack)

    def testDefaultDailyIsDailyInstance(self) -> None:
        """
        Test that the default daily attribute is a Daily instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Channels().daily, Daily)

    def testDictConversion(self) -> None:
        """
        Test that a dict for stack is converted to a Stack instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Channels(stack={"path": "storage/logs/custom.log"})
        self.assertIsInstance(c.stack, Stack)

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Channels instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        c = Channels()
        with self.assertRaises(FrozenInstanceError):
            c.stack = Stack()  # type: ignore[misc]

# ===========================================================================
# Logging entity
# ===========================================================================

class TestLoggingEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Logging can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        log = Logging()
        self.assertIsInstance(log, Logging)

    def testDefaultIsString(self) -> None:
        """
        Test that the default attribute is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Logging().default, str)

    def testDefaultChannelsIsChannelsInstance(self) -> None:
        """
        Test that the channels attribute is a Channels instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Logging().channels, Channels)

    def testInvalidDefaultRaisesValueError(self) -> None:
        """
        Test that an unrecognized default channel name raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Logging(default="nonexistent_channel")

    def testDictChannelsConversion(self) -> None:
        """
        Test that a dict for channels is converted to a Channels instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        log = Logging(channels={})
        self.assertIsInstance(log.channels, Channels)

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Logging instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        log = Logging()
        with self.assertRaises(FrozenInstanceError):
            log.default = "daily"  # type: ignore[misc]
