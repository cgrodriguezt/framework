import re
from orionis.test.cases.synchronous import SyncTestCase
from orionis.support.types.stringable import Stringable


class TestStringableBasic(SyncTestCase):
    """
    Basic test suite for the Stringable class.

    This test suite focuses on core functionality to ensure basic
    operations work correctly without complex edge cases.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates basic Stringable instances for testing core functionality.
        """
        self.basic_string = Stringable("hello world")
        self.empty_string = Stringable("")
        self.mixed_case = Stringable("Hello World")

    def testBasicCreation(self):
        """
        Test basic Stringable creation and string behavior.

        Validates that Stringable objects can be created and behave
        like regular strings.
        """
        s = Stringable("test")
        self.assertEqual(str(s), "test")
        self.assertEqual(len(s), 4)
        self.assertTrue(isinstance(s, str))

    def testAfterMethod(self):
        """
        Test the after method functionality.

        Validates that the after method correctly returns the substring
        after the first occurrence of the search string.
        """
        result = self.basic_string.after("hello ")
        self.assertEqual(result, "world")
        self.assertIsInstance(result, Stringable)

        # Test with non-existent substring
        result = self.basic_string.after("xyz")
        self.assertEqual(result, "hello world")

    def testBeforeMethod(self):
        """
        Test the before method functionality.

        Validates that the before method correctly returns the substring
        before the first occurrence of the search string.
        """
        result = self.basic_string.before(" world")
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, Stringable)

    def testAppendMethod(self):
        """
        Test the append method functionality.

        Validates that strings can be appended correctly.
        """
        result = self.basic_string.append(" test")
        self.assertEqual(result, "hello world test")
        self.assertIsInstance(result, Stringable)

    def testCaseConversion(self):
        """
        Test basic case conversion methods.

        Validates upper, lower, and title case conversions.
        """
        # Test lower
        result = self.mixed_case.lower()
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, Stringable)

        # Test upper
        result = self.mixed_case.upper()
        self.assertEqual(result, "HELLO WORLD")

        # Test title
        result = self.basic_string.title()
        self.assertEqual(result, "Hello World")

    def testContainsMethod(self):
        """
        Test the contains method functionality.

        Validates substring checking with case sensitivity options.
        """
        self.assertTrue(self.basic_string.contains("world"))
        self.assertFalse(self.basic_string.contains("xyz"))
        self.assertTrue(self.basic_string.contains("WORLD", ignore_case=True))

    def testEmptyChecks(self):
        """
        Test empty string checking methods.

        Validates isEmpty and isNotEmpty functionality.
        """
        self.assertTrue(self.empty_string.isEmpty())
        self.assertFalse(self.basic_string.isEmpty())
        self.assertFalse(self.empty_string.isNotEmpty())
        self.assertTrue(self.basic_string.isNotEmpty())

    def testReplaceMethod(self):
        """
        Test the replace method functionality.

        Validates basic string replacement operations.
        """
        result = self.basic_string.replace("world", "universe")
        self.assertEqual(result, "hello universe")
        self.assertIsInstance(result, Stringable)

    def testLength(self):
        """
        Test the length method functionality.

        Validates that length returns correct character count.
        """
        self.assertEqual(self.basic_string.length(), 11)
        self.assertEqual(self.empty_string.length(), 0)

    def testStringConversion(self):
        """
        Test string conversion methods.

        Validates toString and value methods.
        """
        self.assertEqual(self.basic_string.toString(), "hello world")
        self.assertEqual(self.basic_string.value(), "hello world")
        self.assertIsInstance(self.basic_string.toString(), str)