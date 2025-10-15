import re
import json
import base64
import hashlib
from datetime import datetime
from unittest.mock import patch, MagicMock
from orionis.test.cases.synchronous import SyncTestCase
from orionis.support.types.stringable import Stringable


class TestStringable(SyncTestCase):
    """
    Test suite for the Stringable class.

    This comprehensive test suite validates all methods and functionality
    of the Stringable class, ensuring complete compatibility with Laravel's
    Stringable implementation while maintaining Python-specific behavior.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates various Stringable instances used across multiple test methods
        to ensure consistent testing data and reduce code duplication.
        """
        self.basic_string = Stringable("hello world")
        self.empty_string = Stringable("")
        self.mixed_case = Stringable("Hello World")
        self.special_chars = Stringable("hello@world.com")
        self.numeric_string = Stringable("12345")
        self.whitespace_string = Stringable("  hello  world  ")
        self.html_string = Stringable("<p>Hello <strong>World</strong></p>")
        self.json_string = Stringable('{"name": "John", "age": 30}')
        self.url_string = Stringable("https://example.com/path")
        self.uuid_string = Stringable("550e8400-e29b-41d4-a716-446655440000")

    def testAfter(self):
        """
        Test the after method returns substring after first occurrence.

        Validates that the method correctly returns the portion of the string
        that appears after the first occurrence of the search string, or the
        original string if the search string is not found.
        """

        basic_string = Stringable("hello world")

        result = basic_string.after("hello ")
        self.assertEqual(result, "world")
        self.assertIsInstance(result, Stringable)

        # Test with non-existent substring
        result = basic_string.after("xyz")
        self.assertEqual(result, "hello world")

        # Test with empty string
        result = Stringable("").after("test")
        self.assertEqual(result, "")

    def testAfterLast(self):
        """
        Test the afterLast method returns substring after last occurrence.

        Verifies that the method returns the portion of the string after
        the last occurrence of the search string, handling multiple matches
        correctly.
        """
        test_string = Stringable("hello world hello universe")
        result = test_string.afterLast("hello ")
        self.assertEqual(result, "universe")
        self.assertIsInstance(result, Stringable)

        # Test with single occurrence
        basic_string = Stringable("hello world")
        result = basic_string.afterLast("hello ")
        self.assertEqual(result, "world")

        # Test with non-existent substring
        result = basic_string.afterLast("xyz")
        self.assertEqual(result, "hello world")

    def testAppend(self):
        """
        Test the append method adds values to the end of string.

        Validates that single and multiple values can be appended correctly
        and that the original string remains unchanged (immutability).
        """
        basic_string = Stringable("hello world")

        result = basic_string.append(" test")
        self.assertEqual(result, "hello world test")
        self.assertIsInstance(result, Stringable)

        # Test multiple values
        result = basic_string.append(" ", "foo", " ", "bar")
        self.assertEqual(result, "hello world foo bar")

        # Original string should remain unchanged
        self.assertEqual(basic_string, "hello world")

    def testNewLine(self):
        """
        Test the newLine method appends newline characters.

        Verifies that the method correctly appends the specified number
        of newline characters and defaults to one newline when no count
        is provided.
        """
        basic_string = Stringable("hello world")

        result = basic_string.newLine()
        self.assertEqual(result, "hello world\n")
        self.assertIsInstance(result, Stringable)

        # Test multiple newlines
        result = basic_string.newLine(3)
        self.assertEqual(result, "hello world\n\n\n")

        # Test zero newlines
        result = basic_string.newLine(0)
        self.assertEqual(result, "hello world")

    def testBefore(self):
        """
        Test the before method returns substring before first occurrence.

        Validates that the method returns the portion of the string before
        the first occurrence of the search string, or the original string
        if not found.
        """
        basic_string = Stringable("hello world")

        result = basic_string.before(" world")
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, Stringable)

        # Test with non-existent substring
        result = basic_string.before("xyz")
        self.assertEqual(result, "hello world")

        # Test with empty search
        result = basic_string.before("")
        self.assertEqual(result, "")

    def testBeforeLast(self):
        """
        Test the beforeLast method returns substring before last occurrence.

        Verifies that the method correctly handles multiple occurrences
        and returns the portion before the last match.
        """
        test_string = Stringable("hello world hello universe")
        result = test_string.beforeLast(" hello")
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, Stringable)

        # Test with single occurrence
        basic_string = Stringable("hello world")
        result = basic_string.beforeLast(" world")
        self.assertEqual(result, "hello")

    def testContains(self):
        """
        Test the contains method checks for substring presence.

        Validates case-sensitive and case-insensitive searching with
        single strings and arrays of needles.
        """
        basic_string = Stringable("hello world")

        # Test single needle
        self.assertTrue(basic_string.contains("world"))
        self.assertFalse(basic_string.contains("xyz"))

        # Test multiple needles
        self.assertTrue(basic_string.contains(["world", "foo"]))
        self.assertFalse(basic_string.contains(["xyz", "abc"]))

        # Test case insensitive
        self.assertTrue(basic_string.contains("WORLD", ignore_case=True))
        self.assertFalse(basic_string.contains("WORLD", ignore_case=False))

    def testEndsWith(self):
        """
        Test the endsWith method checks string endings.

        Verifies that the method correctly identifies if the string ends
        with any of the provided needles.
        """
        basic_string = Stringable("hello world")
        empty_string = Stringable("")

        self.assertTrue(basic_string.endsWith("world"))
        self.assertFalse(basic_string.endsWith("hello"))

        # Test multiple needles
        self.assertTrue(basic_string.endsWith(["world", "foo"]))
        self.assertFalse(basic_string.endsWith(["foo", "bar"]))

        # Test empty string
        self.assertTrue(empty_string.endsWith(""))

    def testStartsWith(self):
        """
        Test the startsWith method checks string beginnings.

        Validates that the method correctly identifies if the string starts
        with any of the provided needles.
        """
        basic_string = Stringable("hello world")
        empty_string = Stringable("")

        self.assertTrue(basic_string.startsWith("hello"))
        self.assertFalse(basic_string.startsWith("world"))

        # Test multiple needles
        self.assertTrue(basic_string.startsWith(["hello", "foo"]))
        self.assertFalse(basic_string.startsWith(["foo", "bar"]))

        # Test empty string
        self.assertTrue(empty_string.startsWith(""))

    def testExactly(self):
        """
        Test the exactly method performs strict equality comparison.

        Verifies exact string matching with different data types and
        ensures proper type conversion behavior.
        """
        basic_string = Stringable("hello world")
        self.assertTrue(basic_string.exactly("hello world"))
        self.assertFalse(basic_string.exactly("Hello World"))

        # Test with Stringable object
        other_stringable = Stringable("hello world")
        self.assertTrue(basic_string.exactly(other_stringable))

        # Test with number
        number_string = Stringable("123")
        self.assertTrue(number_string.exactly(123))

    def testIsEmpty(self):
        """
        Test the isEmpty method identifies empty strings.

        Validates that the method correctly identifies empty strings
        and distinguishes them from whitespace-only strings.
        """
        empty_string = Stringable("")
        basic_string = Stringable("hello world")
        whitespace_string = Stringable("  hello  world  ")

        self.assertTrue(empty_string.isEmpty())
        self.assertFalse(basic_string.isEmpty())
        self.assertFalse(whitespace_string.isEmpty())

    def testIsNotEmpty(self):
        """
        Test the isNotEmpty method identifies non-empty strings.

        Verifies the inverse behavior of isEmpty method.
        """
        empty_string = Stringable("")
        basic_string = Stringable("hello world")
        whitespace_string = Stringable("  hello  world  ")

        self.assertFalse(empty_string.isNotEmpty())
        self.assertTrue(basic_string.isNotEmpty())
        self.assertTrue(whitespace_string.isNotEmpty())

    def testCaseConversion(self):
        """
        Test case conversion methods (lower, upper, title, etc.).

        Validates all case conversion methods including lower, upper,
        title, camel, snake, kebab, pascal, and studly cases.
        """

        # Test lower
        mixed_case = Stringable("Hello World")
        result = mixed_case.lower()
        assert result == "hello world"
        assert isinstance(result, Stringable)

        # Test upper
        result = mixed_case.upper()
        assert result == "HELLO WORLD"

        # Test title
        basic_string = Stringable("hello world")
        result = basic_string.title()
        assert result == "Hello World"

        # Test camel case
        snake_string = Stringable("hello_world_test")
        result = snake_string.camel()
        assert result == "helloWorldTest"

        # Test snake case
        camel_string = Stringable("helloWorldTest")
        result = camel_string.snake()
        assert result == "hello_world_test"

        # Test kebab case
        result = camel_string.kebab()
        assert result == "hello-world-test"

        # Test studly case
        result = snake_string.studly()
        assert result == "HelloWorldTest"

        # Test pascal case (alias for studly)
        result = snake_string.pascal()
        assert result == "HelloWorldTest"

    def testReverse(self):
        """
        Tests the reverse method for reversing string characters.

        This method verifies that the reverse method correctly reverses the order of characters
        in the string and maintains the Stringable type. It ensures that the reversed string
        matches the expected output and that the returned object is an instance of Stringable.

        Returns
        -------
        None
            This method does not return a value; it asserts correctness using test assertions.
        """

        # Reverse a basic string and check the result
        basic_string = Stringable("hello world")
        result = basic_string.reverse()

        # Assert that the reversed string matches the expected output
        self.assertEqual(result, "dlrow olleh")

        # Assert that the result is an instance of Stringable
        self.assertIsInstance(result, Stringable)

    def testRepeat(self):
        """
        Test the repeat method duplicates the string.

        Verifies that the string is repeated the specified number of times.
        """
        result = Stringable("abc").repeat(3)
        self.assertEqual(result, "abcabcabc")
        self.assertIsInstance(result, Stringable)

        # Test zero repetitions
        result = Stringable("hello world").repeat(0)
        self.assertEqual(result, "")

    def testReplace(self):
        """
        Test the replace method substitutes substrings.

        Validates case-sensitive and case-insensitive replacement with
        single and multiple search/replace pairs.
        """
        basic_string = Stringable("hello world")

        result = basic_string.replace("world", "universe")
        self.assertEqual(result, "hello universe")
        self.assertIsInstance(result, Stringable)

        # Test case insensitive
        result = basic_string.replace("WORLD", "universe", case_sensitive=False)
        self.assertEqual(result, "hello universe")

        # Test multiple replacements
        result = basic_string.replace(["hello", "world"], ["hi", "universe"])
        self.assertEqual(result, "hi universe")

    def testReplaceFirst(self):
        """
        Test the replaceFirst method replaces only first occurrence.

        Verifies that only the first occurrence of the search string
        is replaced, leaving subsequent occurrences unchanged.
        """
        test_string = Stringable("hello world hello universe")
        result = test_string.replaceFirst("hello", "hi")
        self.assertEqual(result, "hi world hello universe")
        self.assertIsInstance(result, Stringable)

    def testReplaceLast(self):
        """
        Test the replaceLast method replaces only last occurrence.

        Validates that only the last occurrence of the search string
        is replaced.
        """
        test_string = Stringable("hello world hello universe")
        result = test_string.replaceLast("hello", "hi")
        self.assertEqual(result, "hello world hi universe")
        self.assertIsInstance(result, Stringable)

    def testStripTags(self):
        """
        Test the stripTags method removes HTML tags.

        Verifies that HTML tags are properly removed while preserving
        the text content.
        """
        html_string = Stringable("<p>Hello <strong>World</strong></p>")
        result = html_string.stripTags()
        self.assertEqual(result, "Hello World")
        self.assertIsInstance(result, Stringable)

        # Test with PHP tags
        php_string = Stringable("<?php echo 'Hello'; ?> <b>World</b>")
        result = php_string.stripTags().trim()
        self.assertEqual(result, "World")
        self.assertIsInstance(result, Stringable)

    def testBase64Encoding(self):
        """
        Test Base64 encoding and decoding methods.

        Validates that strings can be properly encoded to and decoded
        from Base64 format.
        """
        basic_string = Stringable("hello world")

        # Test encoding
        encoded = basic_string.toBase64()
        self.assertEqual(encoded, "aGVsbG8gd29ybGQ=")
        self.assertIsInstance(encoded, Stringable)

        # Test decoding
        decoded = encoded.fromBase64()
        self.assertEqual(decoded, "hello world")
        self.assertIsInstance(decoded, Stringable)

        # Test strict decoding with invalid base64
        invalid_b64 = Stringable("invalid!@#")
        result = invalid_b64.fromBase64(strict=False)
        self.assertEqual(result, "")

    # def testHashMethods(self):
    #     """
    #     Test hash generation methods (MD5, SHA1, SHA256).

    #     Validates that all hash methods produce correct hash values
    #     for the input strings.
    #     """
    #     # Test MD5
    #     md5_hash = self.basic_string.md5()
    #     expected_md5 = hashlib.md5("hello world".encode()).hexdigest()
    #     self.assertEqual(md5_hash, expected_md5)

    #     # Test SHA1
    #     sha1_hash = self.basic_string.sha1()
    #     expected_sha1 = hashlib.sha1("hello world".encode()).hexdigest()
    #     self.assertEqual(sha1_hash, expected_sha1)

    #     # Test SHA256
    #     sha256_hash = self.basic_string.sha256()
    #     expected_sha256 = hashlib.sha256("hello world".encode()).hexdigest()
    #     self.assertEqual(sha256_hash, expected_sha256)

    # def testLength(self):
    #     """
    #     Test the length method returns correct string length.

    #     Validates that the method returns the correct number of characters
    #     in the string.
    #     """
    #     self.assertEqual(self.basic_string.length(), 11)
    #     self.assertEqual(self.empty_string.length(), 0)
    #     self.assertEqual(self.numeric_string.length(), 5)

    # def testValueAndToString(self):
    #     """
    #     Test value and toString methods return string representation.

    #     Verifies that both methods return the correct string value.
    #     """
    #     self.assertEqual(self.basic_string.value(), "hello world")
    #     self.assertEqual(self.basic_string.toString(), "hello world")
    #     self.assertIsInstance(self.basic_string.value(), str)
    #     self.assertIsInstance(self.basic_string.toString(), str)

    # def testTypeConversions(self):
    #     """
    #     Test type conversion methods (toInteger, toFloat, toBoolean).

    #     Validates conversion to different Python types with appropriate
    #     error handling for invalid conversions.
    #     """
    #     # Test toInteger
    #     result = self.numeric_string.toInteger()
    #     self.assertEqual(result, 12345)
    #     self.assertIsInstance(result, int)

    #     # Test toInteger with base
    #     hex_string = Stringable("ff")
    #     result = hex_string.toInteger(16)
    #     self.assertEqual(result, 255)

    #     # Test toFloat
    #     float_string = Stringable("123.45")
    #     result = float_string.toFloat()
    #     self.assertEqual(result, 123.45)
    #     self.assertIsInstance(result, float)

    #     # Test toBoolean
    #     true_strings = ["1", "true", "on", "yes"]
    #     for true_str in true_strings:
    #         self.assertTrue(Stringable(true_str).toBoolean())

    #     false_strings = ["0", "false", "off", "no", ""]
    #     for false_str in false_strings:
    #         self.assertFalse(Stringable(false_str).toBoolean())

    # def testValidationMethods(self):
    #     """
    #     Test string validation methods (isAscii, isJson, isUrl, etc.).

    #     Validates various string format validation methods including
    #     ASCII, JSON, URL, UUID, and ULID validation.
    #     """
    #     # Test isAscii
    #     self.assertTrue(self.basic_string.isAscii())
    #     unicode_string = Stringable("héllo wörld")
    #     self.assertFalse(unicode_string.isAscii())

    #     # Test isJson
    #     self.assertTrue(self.json_string.isJson())
    #     self.assertFalse(self.basic_string.isJson())

    #     # Test isUrl
    #     self.assertTrue(self.url_string.isUrl())
    #     self.assertFalse(self.basic_string.isUrl())

    #     # Test isUuid - basic format check
    #     self.assertTrue(self.uuid_string.isUuid())
    #     self.assertFalse(self.basic_string.isUuid())

    #     # Test isUlid - basic format check
    #     ulid_string = Stringable("01ARZ3NDEKTSV4RRFFQ69G5FAV")
    #     self.assertTrue(ulid_string.isUlid())
    #     self.assertFalse(self.basic_string.isUlid())

    # def testStringManipulation(self):
    #     """
    #     Test string manipulation methods (trim, pad, mask, etc.).

    #     Validates various string manipulation operations including
    #     trimming, padding, masking, and limiting.
    #     """
    #     # Test trim methods
    #     result = self.whitespace_string.trim()
    #     self.assertEqual(result, "hello  world")
    #     self.assertIsInstance(result, Stringable)

    #     result = self.whitespace_string.ltrim()
    #     self.assertEqual(result, "hello  world  ")

    #     result = self.whitespace_string.rtrim()
    #     self.assertEqual(result, "  hello  world")

    #     # Test padding methods
    #     short_string = Stringable("hi")
    #     result = short_string.padBoth(10, "*")
    #     self.assertEqual(result, "****hi****")

    #     result = short_string.padLeft(5, "0")
    #     self.assertEqual(result, "000hi")

    #     result = short_string.padRight(5, "0")
    #     self.assertEqual(result, "hi000")

    #     # Test mask
    #     secret = Stringable("1234567890")
    #     result = secret.mask("*", 2, 6)
    #     self.assertEqual(result, "12******90")

    #     # Test limit
    #     long_string = Stringable("This is a very long string that should be limited")
    #     result = long_string.limit(20)
    #     self.assertEqual(result, "This is a very long ...")

    #     result = long_string.limit(20, preserve_words=True)
    #     self.assertTrue(len(result) <= 23)  # Account for word boundaries

    # def testPatternMatching(self):
    #     """
    #     Test pattern matching methods (match, matchAll, isMatch, test).

    #     Validates regular expression matching capabilities and pattern
    #     validation methods.
    #     """
    #     email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    #     # Test match
    #     result = self.special_chars.match(email_pattern)
    #     self.assertEqual(result, "hello@world.com")
    #     self.assertIsInstance(result, Stringable)

    #     # Test matchAll
    #     multi_email = Stringable("Contact: john@example.com or jane@test.org")
    #     result = multi_email.matchAll(email_pattern)
    #     self.assertEqual(len(result), 2)
    #     self.assertIn("john@example.com", result)
    #     self.assertIn("jane@test.org", result)

    #     # Test isMatch
    #     self.assertTrue(self.special_chars.isMatch(email_pattern))
    #     self.assertFalse(self.basic_string.isMatch(email_pattern))

    #     # Test test (alias for isMatch)
    #     self.assertTrue(self.special_chars.test(email_pattern))

    #     # Test isPattern (wildcard matching)
    #     self.assertTrue(self.basic_string.isPattern("hello*"))
    #     self.assertTrue(self.basic_string.isPattern("*world"))
    #     self.assertFalse(self.basic_string.isPattern("foo*"))

    # def testWordOperations(self):
    #     """
    #     Test word-related operations (words, wordCount, wordWrap).

    #     Validates methods that operate on word boundaries including
    #     limiting words, counting words, and wrapping text.
    #     """
    #     long_text = Stringable("This is a long sentence with many words to test")

    #     # Test words
    #     result = long_text.words(5)
    #     self.assertEqual(result, "This is a long sentence...")

    #     # Test wordCount
    #     self.assertEqual(long_text.wordCount(), 10)

    #     # Test wordWrap
    #     result = long_text.wordWrap(20)
    #     self.assertIn("\n", result)
    #     self.assertIsInstance(result, Stringable)

    # def testArrayOperations(self):
    #     """
    #     Test array-like operations (explode, split, ucsplit).

    #     Validates methods that split strings into arrays or lists
    #     based on different criteria.
    #     """
    #     csv_string = Stringable("apple,banana,cherry")

    #     # Test explode
    #     result = csv_string.explode(",")
    #     self.assertEqual(result, ["apple", "banana", "cherry"])

    #     # Test explode with limit
    #     result = csv_string.explode(",", 2)
    #     self.assertEqual(result, ["apple", "banana,cherry"])

    #     # Test split with regex
    #     result = csv_string.split(r"[,]")
    #     self.assertEqual(result, ["apple", "banana", "cherry"])

    #     # Test split by length
    #     result = Stringable("abcdef").split(2)
    #     self.assertEqual(result, ["ab", "cd", "ef"])

    #     # Test ucsplit
    #     camel_string = Stringable("HelloWorldTest")
    #     result = camel_string.ucsplit()
    #     self.assertEqual(result, ["Hello", "World", "Test"])

    # def testConditionalMethods(self):
    #     """
    #     Test conditional execution methods (when, whenEmpty, etc.).

    #     Validates that conditional methods execute callbacks correctly
    #     based on string state and conditions.
    #     """
    #     # Test when with True condition
    #     result = self.basic_string.when(True, lambda s: s.upper())
    #     self.assertEqual(result, "HELLO WORLD")

    #     # Test when with False condition and default
    #     result = self.basic_string.when(False, lambda s: s.upper(), lambda s: s.lower())
    #     self.assertEqual(result, "hello world")

    #     # Test whenEmpty
    #     result = self.empty_string.whenEmpty(lambda s: Stringable("default"))
    #     self.assertEqual(result, "default")

    #     result = self.basic_string.whenEmpty(lambda s: Stringable("default"))
    #     self.assertEqual(result, "hello world")

    #     # Test whenNotEmpty
    #     result = self.basic_string.whenNotEmpty(lambda s: s.upper())
    #     self.assertEqual(result, "HELLO WORLD")

    #     # Test whenContains
    #     result = self.basic_string.whenContains("world", lambda s: s.upper())
    #     self.assertEqual(result, "HELLO WORLD")

    #     # Test whenStartsWith
    #     result = self.basic_string.whenStartsWith("hello", lambda s: s.title())
    #     self.assertEqual(result, "Hello World")

    #     # Test whenEndsWith
    #     result = self.basic_string.whenEndsWith("world", lambda s: s.reverse())
    #     self.assertEqual(result, "dlrow olleh")

    # def testPluralization(self):
    #     """
    #     Test pluralization methods (plural, singular, pluralStudly).

    #     Validates English pluralization and singularization with
    #     different count parameters.
    #     """
    #     # Test basic plural - simplified to avoid complex pluralization logic
    #     singular = Stringable("user")
    #     result = singular.plural()
    #     self.assertIsInstance(result, Stringable)
    #     # Most words just add 's' for basic cases
    #     self.assertTrue(str(result).endswith("s"))

    #     result = singular.plural(1)
    #     self.assertEqual(result, "user")

    #     # Test singular - basic test
    #     plural = Stringable("users")
    #     result = plural.singular()
    #     self.assertIsInstance(result, Stringable)
    #     # Basic singularization removes trailing 's'
    #     self.assertEqual(result, "user")

    # def testUtilityMethods(self):
    #     """
    #     Test utility methods (pipe, tap, take, swap, etc.).

    #     Validates various utility methods that provide additional
    #     functionality for string processing.
    #     """
    #     # Test pipe
    #     result = self.basic_string.pipe(lambda s: s.upper().replace(" ", "_"))
    #     self.assertEqual(result, "HELLO_WORLD")
    #     self.assertIsInstance(result, Stringable)

    #     # Test tap
    #     tapped_value = None
    #     def tap_callback(s):
    #         nonlocal tapped_value
    #         tapped_value = str(s)

    #     result = self.basic_string.tap(tap_callback)
    #     self.assertEqual(result, self.basic_string)
    #     self.assertEqual(tapped_value, "hello world")

    #     # Test take
    #     result = self.basic_string.take(5)
    #     self.assertEqual(result, "hello")

    #     result = self.basic_string.take(-5)
    #     self.assertEqual(result, "world")

    #     # Test swap
    #     result = self.basic_string.swap({"hello": "hi", "world": "universe"})
    #     self.assertEqual(result, "hi universe")

    # def testAdvancedFeatures(self):
    #     """
    #     Test advanced features (toDate, encrypt/decrypt, etc.).

    #     Validates advanced functionality including date parsing,
    #     encryption placeholders, and HTML string creation.
    #     """
    #     # Test toDate - basic test
    #     date_string = Stringable("2024-01-15")
    #     result = date_string.toDate()
    #     if result is not None:  # Only test if parsing succeeds
    #         self.assertIsInstance(result, datetime)
    #         self.assertEqual(result.year, 2024)

    #     # Test encrypt/decrypt (placeholder implementation)
    #     encrypted = self.basic_string.encrypt()
    #     decrypted = encrypted.decrypt()
    #     self.assertEqual(decrypted, "hello world")

    #     # Test toHtmlString
    #     html_result = self.html_string.toHtmlString()
    #     self.assertIn("&lt;", html_result)
    #     self.assertIn("&gt;", html_result)

    # def testEdgeCases(self):
    #     """
    #     Test edge cases and boundary conditions.

    #     Validates behavior with empty strings, None values, and
    #     extreme input conditions.
    #     """
    #     # Test with empty string
    #     empty = Stringable("")
    #     self.assertEqual(empty.after("test"), "")
    #     self.assertEqual(empty.before("test"), "")
    #     self.assertEqual(empty.replace("old", "new"), "")
    #     self.assertTrue(empty.isEmpty())

    #     # Test with very long string
    #     long_string = Stringable("a" * 10000)
    #     self.assertEqual(len(long_string), 10000)
    #     self.assertEqual(long_string.take(5), "aaaaa")

    #     # Test with special characters
    #     special = Stringable("!@#$%^&*()")
    #     self.assertEqual(special.length(), 10)
    #     self.assertTrue(special.isNotEmpty())

    #     # Test with unicode
    #     unicode_string = Stringable("héllo wörld 🌍")
    #     self.assertFalse(unicode_string.isAscii())
    #     self.assertEqual(unicode_string.length(), 14)

    # def testTypeCompatibility(self):
    #     """
    #     Test type compatibility and string protocol implementation.

    #     Validates that Stringable behaves correctly as a string subclass
    #     and implements the expected protocols.
    #     """
    #     # Test string comparison
    #     self.assertEqual(self.basic_string, "hello world")
    #     self.assertTrue(self.basic_string == "hello world")

    #     # Test iteration
    #     chars = list(self.basic_string)
    #     self.assertEqual(len(chars), 11)
    #     self.assertEqual(chars[0], "h")

    #     # Test indexing
    #     self.assertEqual(self.basic_string[0], "h")
    #     self.assertEqual(self.basic_string[-1], "d")

    #     # Test slicing returns Stringable
    #     result = self.basic_string[0:5]
    #     self.assertEqual(result, "hello")
    #     self.assertIsInstance(result, Stringable)

    #     # Test string methods still work
    #     self.assertTrue(self.basic_string.startswith("hello"))
    #     self.assertTrue(self.basic_string.endswith("world"))

    # def testAliasCompatibility(self):
    #     """
    #     Test backwards compatibility aliases.

    #     Validates that snake_case aliases work correctly and maintain
    #     backwards compatibility.
    #     """
    #     # Test snake_case aliases
    #     self.assertEqual(self.empty_string.is_empty(), True)
    #     self.assertEqual(self.basic_string.is_not_empty(), True)
    #     self.assertEqual(self.basic_string.ends_with("world"), True)
    #     self.assertEqual(self.html_string.strip_tags(), "Hello World")
    #     self.assertEqual(self.basic_string.to_base64(), "aGVsbG8gd29ybGQ=")

    # def testJsonSerialization(self):
    #     """
    #     Test JSON serialization support.

    #     Validates that Stringable objects can be properly serialized
    #     to JSON format.
    #     """
    #     result = self.basic_string.jsonSerialize()
    #     self.assertEqual(result, "hello world")
    #     self.assertIsInstance(result, str)

    # def testArrayAccess(self):
    #     """
    #     Test array access implementation.

    #     Validates that Stringable implements array access protocols
    #     correctly for character-level access.
    #     """
    #     # Test offsetExists
    #     self.assertTrue(self.basic_string.offsetExists(0))
    #     self.assertTrue(self.basic_string.offsetExists(10))
    #     self.assertFalse(self.basic_string.offsetExists(11))

    #     # Test offsetGet
    #     self.assertEqual(self.basic_string.offsetGet(0), "h")
    #     self.assertEqual(self.basic_string.offsetGet(6), "w")

    # @patch('builtins.print')
    # def testDumpMethods(self, mock_print):
    #     """
    #     Test dump and dd methods for debugging.

    #     Validates that dump methods correctly output values and
    #     that dd method terminates execution.

    #     Parameters
    #     ----------
    #     mock_print : Mock
    #         Mocked print function to capture output
    #     """
    #     # Test dump
    #     result = self.basic_string.dump("extra", "args")
    #     self.assertEqual(result, self.basic_string)
    #     mock_print.assert_called_with("hello world", "extra", "args")

    #     # Test dd (should call sys.exit)
    #     with patch('sys.exit') as mock_exit:
    #         self.basic_string.dd("debug", "info")
    #         mock_exit.assert_called_once_with(1)

    # def testChainability(self):
    #     """
    #     Test method chaining capabilities.

    #     Validates that methods can be chained together effectively
    #     and that each method returns a Stringable instance.
    #     """
    #     result = (self.basic_string
    #              .replace("world", "universe")
    #              .upper()
    #              .append("!")
    #              .trim())

    #     self.assertEqual(result, "HELLO UNIVERSE!")
    #     self.assertIsInstance(result, Stringable)

    #     # Test complex chain
    #     complex_result = (Stringable("  hello_world  ")
    #                      .trim()
    #                      .camel()
    #                      .ucfirst()
    #                      .append("Class"))

    #     self.assertEqual(complex_result, "HelloWorldClass")

    # def testErrorHandling(self):
    #     """
    #     Test error handling in various methods.

    #     Validates that methods handle invalid input gracefully
    #     and provide appropriate error handling.
    #     """
    #     # Test invalid base64 with strict mode
    #     invalid_b64 = Stringable("invalid!@#")
    #     with self.assertRaises(Exception):
    #         invalid_b64.fromBase64(strict=True)

    #     # Test invalid date format
    #     invalid_date = Stringable("not-a-date")
    #     result = invalid_date.toDate()
    #     self.assertIsNone(result)

    #     # Test invalid numeric conversion
    #     with self.assertRaises(ValueError):
    #         self.basic_string.toInteger()

    #     with self.assertRaises(ValueError):
    #         self.basic_string.toFloat()
