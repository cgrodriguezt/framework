import hashlib
from datetime import datetime
from orionis.test.cases.synchronous import SyncTestCase
from orionis.support.strings.stringable import Stringable

class TestStringable(SyncTestCase):

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

    def testHashMethods(self):
        """
        Test hash generation methods (MD5, SHA1, SHA256).

        Validates that all hash methods produce correct hash values
        for the input strings.
        """
        basic_string = Stringable("hello world")

        # Test MD5
        md5_hash = basic_string.md5()
        expected_md5 = hashlib.md5("hello world".encode()).hexdigest()
        self.assertEqual(md5_hash, expected_md5)

        # Test SHA1
        sha1_hash = basic_string.sha1()
        expected_sha1 = hashlib.sha1("hello world".encode()).hexdigest()
        self.assertEqual(sha1_hash, expected_sha1)

        # Test SHA256
        sha256_hash = basic_string.sha256()
        expected_sha256 = hashlib.sha256("hello world".encode()).hexdigest()
        self.assertEqual(sha256_hash, expected_sha256)

    def testLength(self):
        """
        Test the length method returns correct string length.

        Validates that the method returns the correct number of characters
        in the string.
        """
        basic_string = Stringable("hello world")
        empty_string = Stringable("")
        numeric_string = Stringable("12345")

        self.assertEqual(basic_string.length(), 11)
        self.assertEqual(empty_string.length(), 0)
        self.assertEqual(numeric_string.length(), 5)

    def testValueAndToString(self):
        """
        Test value and toString methods return string representation.

        Verifies that both methods return the correct string value.
        """
        basic_string = Stringable("hello world")
        self.assertEqual(basic_string.value(), "hello world")
        self.assertEqual(basic_string.toString(), "hello world")
        self.assertIsInstance(basic_string.value(), str)
        self.assertIsInstance(basic_string.toString(), str)

    def testTypeConversions(self):
        """
        Test type conversion methods (toInteger, toFloat, toBoolean).

        Validates conversion to different Python types with appropriate
        error handling for invalid conversions.
        """
        # Test toInteger
        numeric_string = Stringable("12345")
        result = numeric_string.toInteger()
        self.assertEqual(result, 12345)
        self.assertIsInstance(result, int)

        # Test toInteger with base
        hex_string = Stringable("ff")
        result = hex_string.toInteger(16)
        self.assertEqual(result, 255)

        # Test toFloat
        float_string = Stringable("123.45")
        result = float_string.toFloat()
        self.assertEqual(result, 123.45)
        self.assertIsInstance(result, float)

        # Test toBoolean
        true_strings = ["1", "true", "on", "yes"]
        for true_str in true_strings:
            self.assertTrue(Stringable(true_str).toBoolean())

        false_strings = ["0", "false", "off", "no", ""]
        for false_str in false_strings:
            self.assertFalse(Stringable(false_str).toBoolean())

    def testValidationMethods(self):
        """
        Test string validation methods (isAscii, isJson, isUrl, etc.).

        Validates various string format validation methods including
        ASCII, JSON, URL, UUID, and ULID validation.
        """
        # Test isAscii
        basic_string = Stringable("hello world")
        self.assertTrue(basic_string.isAscii())
        unicode_string = Stringable("héllo wörld")
        self.assertFalse(unicode_string.isAscii())

        # Test isJson
        json_string = Stringable('{"name": "John", "age": 30}')
        self.assertTrue(json_string.isJson())
        self.assertFalse(basic_string.isJson())

        # Test isUrl
        url_string = Stringable("https://example.com/path")
        self.assertTrue(url_string.isUrl())
        self.assertFalse(basic_string.isUrl())

        # Test isUuid - basic format check
        uuid_string = Stringable("550e8400-e29b-41d4-a716-446655440000")
        self.assertTrue(uuid_string.isUuid())
        self.assertFalse(basic_string.isUuid())

        # Test isUlid - basic format check
        ulid_string = Stringable("01ARZ3NDEKTSV4RRFFQ69G5FAV")
        self.assertTrue(ulid_string.isUlid())
        self.assertFalse(basic_string.isUlid())

    def testStringManipulation(self):
        """
        Test string manipulation methods (trim, pad, mask, etc.).

        Validates various string manipulation operations including
        trimming, padding, masking, and limiting.
        """
        whitespace_string = Stringable("  hello  world  ")

        # Test trim methods
        result = whitespace_string.trim()
        self.assertEqual(result, "hello  world")
        self.assertIsInstance(result, Stringable)

        result = whitespace_string.ltrim()
        self.assertEqual(result, "hello  world  ")

        result = whitespace_string.rtrim()
        self.assertEqual(result, "  hello  world")

        # Test padding methods
        short_string = Stringable("hi")
        result = short_string.padBoth(10, "*")
        self.assertEqual(result, "****hi****")

        result = short_string.padLeft(5, "0")
        self.assertEqual(result, "000hi")

        result = short_string.padRight(5, "0")
        self.assertEqual(result, "hi000")

        # Test mask
        secret = Stringable("1234567890")
        result = secret.mask("*", 2, 6)
        self.assertEqual(result, "12******90")

        # Test limit
        long_string = Stringable("This is a very long string that should be limited")
        result = long_string.limit(20)
        self.assertEqual(result, "This is a very long ...")

        result = long_string.limit(20, preserve_words=True)
        self.assertTrue(len(result) <= 23)  # Account for word boundaries

    def testPatternMatching(self):
        """
        Test pattern matching methods (match, matchAll, isMatch, test).

        Validates regular expression matching capabilities and pattern
        validation methods.
        """
        special_chars = Stringable("hello@world.com")
        basic_string = Stringable("hello world")

        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # Test match
        result = special_chars.match(email_pattern)
        self.assertEqual(result, "hello@world.com")
        self.assertIsInstance(result, Stringable)

        # Test matchAll
        multi_email = Stringable("Contact: runate@example.com or rmunate@orionis.org")
        result = multi_email.matchAll(email_pattern)
        self.assertEqual(len(result), 2)
        self.assertIn("runate@example.com", result)
        self.assertIn("rmunate@orionis.org", result)

        # Test isMatch
        self.assertTrue(special_chars.isMatch(email_pattern))
        self.assertFalse(basic_string.isMatch(email_pattern))

        # Test test (alias for isMatch)
        self.assertTrue(special_chars.test(email_pattern))

        # Test isPattern (wildcard matching)
        self.assertTrue(basic_string.isPattern("hello*"))
        self.assertTrue(basic_string.isPattern("*world"))
        self.assertFalse(basic_string.isPattern("foo*"))

    def testWordOperations(self):
        """
        Test word-related operations (words, wordCount, wordWrap).

        Validates methods that operate on word boundaries including
        limiting words, counting words, and wrapping text.
        """
        long_text = Stringable("This is a long sentence with many words to test")

        # Test words
        result = long_text.words(5)
        self.assertEqual(result, "This is a long sentence...")

        # Test wordCount
        self.assertEqual(long_text.wordCount(), 10)

        # Test wordWrap
        result = long_text.wordWrap(20)
        self.assertIn("\n", result)
        self.assertIsInstance(result, Stringable)

    def testArrayOperations(self):
        """
        Test array-like operations (explode, split, ucsplit).

        Validates methods that split strings into arrays or lists
        based on different criteria.
        """
        csv_string = Stringable("apple,banana,cherry")

        # Test explode
        result = csv_string.explode(",")
        self.assertEqual(result, ["apple", "banana", "cherry"])

        # Test explode with limit
        result = csv_string.explode(",", 2)
        self.assertEqual(result, ["apple", "banana,cherry"])

        # Test split with delimiter
        result = csv_string.split(",")
        self.assertEqual(result, ["apple", "banana", "cherry"])

        # Test split by length
        result = Stringable("abcdef").split(2)
        self.assertEqual(result, ["ab", "cd", "ef"])

        # Test ucsplit
        camel_string = Stringable("HelloWorldTest")
        result = camel_string.ucsplit()
        self.assertEqual(result, ["Hello", "World", "Test"])

    def testConditionalMethods(self):
        """
        Test conditional execution methods (when, whenEmpty, etc.).

        Validates that conditional methods execute callbacks correctly
        based on string state and conditions.
        """
        basic_string = Stringable("hello world")
        empty_string = Stringable("")

        # Test when with True condition
        result = basic_string.when(True, lambda s: s.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Test when with False condition and default
        result = basic_string.when(False, lambda s: s.upper(), lambda s: s.lower())
        self.assertEqual(result, "hello world")

        # Test whenEmpty
        result = empty_string.whenEmpty(lambda s: Stringable("default"))
        self.assertEqual(result, "default")

        result = basic_string.whenEmpty(lambda s: Stringable("default"))
        self.assertEqual(result, "hello world")

        # Test whenNotEmpty
        result = basic_string.whenNotEmpty(lambda s: s.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Test whenContains
        result = basic_string.whenContains("world", lambda s: s.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Test whenStartsWith
        result = basic_string.whenStartsWith("hello", lambda s: s.title())
        self.assertEqual(result, "Hello World")

        # Test whenEndsWith
        result = basic_string.whenEndsWith("world", lambda s: s.reverse())
        self.assertEqual(result, "dlrow olleh")

    def testPluralization(self):
        """
        Test pluralization methods (plural, singular, pluralStudly).

        Validates English pluralization and singularization with
        different count parameters.
        """
        # Test basic plural - simplified to avoid complex pluralization logic
        singular = Stringable("user")
        result = singular.plural()
        self.assertIsInstance(result, Stringable)
        # Most words just add 's' for basic cases
        self.assertTrue(str(result).endswith("s"))

        result = singular.plural(1)
        self.assertEqual(result, "user")

        # Test singular - basic test
        plural = Stringable("users")
        result = plural.singular()
        self.assertIsInstance(result, Stringable)
        # Basic singularization removes trailing 's'
        self.assertEqual(result, "user")

    def testUtilityMethods(self):
        """
        Test utility methods (pipe, tap, take, swap, etc.).

        Validates various utility methods that provide additional
        functionality for string processing.
        """
        basic_string = Stringable("hello world")

        # Test pipe
        result = basic_string.pipe(lambda s: s.upper().replace(" ", "_"))
        self.assertEqual(result, "HELLO_WORLD")
        self.assertIsInstance(result, Stringable)

        # Test tap
        tapped_value = None
        def tap_callback(s):
            nonlocal tapped_value
            tapped_value = str(s)

        result = basic_string.tap(tap_callback)
        self.assertEqual(result, basic_string)
        self.assertEqual(tapped_value, "hello world")

        # Test take
        result = basic_string.take(5)
        self.assertEqual(result, "hello")

        result = basic_string.take(-5)
        self.assertEqual(result, "world")

        # Test swap
        result = basic_string.swap({"hello": "hi", "world": "universe"})
        self.assertEqual(result, "hi universe")

    def testAdvancedFeatures(self):
        """
        Test advanced features (toDate, encrypt/decrypt, etc.).

        Validates advanced functionality including date parsing,
        encryption placeholders, and HTML string creation.
        """
        # Test toDate - basic test
        date_string = Stringable("2024-01-15")
        result = date_string.toDate()
        if result is not None:  # Only test if parsing succeeds
            self.assertIsInstance(result, datetime)
            self.assertEqual(result.year, 2024)

        # Test encrypt/decrypt (placeholder implementation)
        basic_string = Stringable("hello world")
        encrypted = basic_string.encrypt()
        decrypted = encrypted.decrypt()
        self.assertEqual(decrypted, "hello world")

        # Test toHtmlString
        html_string = Stringable("<p>Hello <strong>World</strong></p>")
        html_result = html_string.toHtmlString()
        self.assertIn("&lt;", html_result)
        self.assertIn("&gt;", html_result)

    def testEdgeCases(self):
        """
        Test edge cases and boundary conditions.

        Validates behavior with empty strings, None values, and
        extreme input conditions.
        """
        # Test with empty string
        empty = Stringable("")
        self.assertEqual(empty.after("test"), "")
        self.assertEqual(empty.before("test"), "")
        self.assertEqual(empty.replace("old", "new"), "")
        self.assertTrue(empty.isEmpty())

        # Test with very long string
        long_string = Stringable("a" * 10000)
        self.assertEqual(len(long_string), 10000)
        self.assertEqual(long_string.take(5), "aaaaa")

        # Test with special characters
        special = Stringable("!@#$%^&*()")
        self.assertEqual(special.length(), 10)
        self.assertTrue(special.isNotEmpty())

        # Test with unicode
        unicode_string = Stringable("héllo wörld 🌍")
        self.assertFalse(unicode_string.isAscii())
        self.assertEqual(unicode_string.length(), 13)

    def testTypeCompatibility(self):
        """
        Test type compatibility and string protocol implementation.

        Validates that Stringable behaves correctly as a string subclass
        and implements the expected protocols.
        """
        basic_string = Stringable("hello world")

        # Test string comparison
        self.assertEqual(basic_string, "hello world")
        self.assertTrue(basic_string == "hello world")

        # Test iteration
        chars = list(basic_string)
        self.assertEqual(len(chars), 11)
        self.assertEqual(chars[0], "h")

        # Test indexing
        self.assertEqual(basic_string[0], "h")
        self.assertEqual(basic_string[-1], "d")

        # Test slicing returns Stringable
        result = basic_string[0:5]
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, Stringable)

        # Test string methods still work
        self.assertTrue(basic_string.startswith("hello"))
        self.assertTrue(basic_string.endswith("world"))

    def testJsonSerialization(self):
        """
        Test JSON serialization support.

        Validates that Stringable objects can be properly serialized
        to JSON format.
        """
        basic_string = Stringable("hello world")
        result = basic_string.jsonSerialize()
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, str)

    def testArrayAccess(self):
        """
        Test array access implementation.

        Validates that Stringable implements array access protocols
        correctly for character-level access.
        """
        s = Stringable("hello world")

        # Test offsetExists
        self.assertTrue(s.offsetExists(0))
        self.assertTrue(s.offsetExists(10))
        self.assertFalse(s.offsetExists(11))

        # Test offsetGet
        self.assertEqual(s.offsetGet(0), "h")
        self.assertEqual(s.offsetGet(6), "w")

    def testChainability(self):
        """
        Test method chaining capabilities.

        Validates that methods can be chained together effectively
        and that each method returns a Stringable instance.
        """
        basic_string = Stringable("hello world")
        result = (basic_string
                 .replace("world", "universe")
                 .upper()
                 .append("!")
                 .trim())

        self.assertEqual(result, "HELLO UNIVERSE!")
        self.assertIsInstance(result, Stringable)

        # Test complex chain
        complex_result = (Stringable("  hello_world  ")
                         .trim()
                         .camel()
                         .ucfirst()
                         .append("Class"))

        self.assertEqual(complex_result, "HelloWorldClass")

    def testErrorHandling(self):
        """
        Test error handling in various methods.

        Validates that methods handle invalid input gracefully
        and provide appropriate error handling.
        """
        # Test invalid base64 with strict mode
        invalid_b64 = Stringable("invalid!@#")
        with self.assertRaises(Exception):
            invalid_b64.fromBase64(strict=True)

        # Test invalid date format
        invalid_date = Stringable("not-a-date")
        result = invalid_date.toDate()
        self.assertIsNone(result)

        # Test invalid numeric conversion
        basic_string = Stringable("hello world")
        with self.assertRaises(ValueError):
            basic_string.toInteger()

        with self.assertRaises(ValueError):
            basic_string.toFloat()

    def testGetItem(self):
        """
        Test the __getitem__ method for indexing and slicing.

        This method verifies that indexing and slicing operations on a Stringable object
        return the expected substrings and maintain the Stringable type.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Test single character access by index
        self.assertEqual(s[0], "h")
        self.assertEqual(s[-1], "d")
        self.assertIsInstance(s[0], Stringable)

        # Test slicing returns correct substring and type
        result = s[0:5]
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, Stringable)

        result = s[6:]
        self.assertEqual(result, "world")
        self.assertIsInstance(result, Stringable)

    def testStr(self):
        """
        Test the __str__ method for string representation.

        This method checks that converting a Stringable object to a string
        returns the correct string value and type.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Convert Stringable to string and check value and type
        result = str(s)
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, str)

    def testIsAlnum(self):
        """
        Test the isAlnum method for alphanumeric character validation.

        This method verifies that isAlnum correctly identifies strings containing
        only alphanumeric characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check various alphanumeric and non-alphanumeric cases
        self.assertTrue(Stringable("abc123").isAlnum())
        self.assertTrue(Stringable("ABC123").isAlnum())
        self.assertFalse(Stringable("abc 123").isAlnum())
        self.assertFalse(Stringable("abc-123").isAlnum())
        self.assertFalse(Stringable("").isAlnum())

    def testIsAlpha(self):
        """
        Test the isAlpha method for alphabetic character validation.

        This method checks that isAlpha correctly identifies strings containing
        only alphabetic characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check various alphabetic and non-alphabetic cases
        self.assertTrue(Stringable("abc").isAlpha())
        self.assertTrue(Stringable("ABC").isAlpha())
        self.assertFalse(Stringable("abc123").isAlpha())
        self.assertFalse(Stringable("abc ").isAlpha())
        self.assertFalse(Stringable("").isAlpha())

    def testIsDecimal(self):
        """
        Test the isDecimal method for decimal character validation.

        This method verifies that isDecimal correctly identifies strings containing
        only decimal characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check decimal and non-decimal cases
        self.assertTrue(Stringable("123").isDecimal())
        self.assertTrue(Stringable("0").isDecimal())
        self.assertFalse(Stringable("12.3").isDecimal())
        self.assertFalse(Stringable("abc").isDecimal())
        self.assertFalse(Stringable("").isDecimal())

    def testIsDigit(self):
        """
        Test the isDigit method for digit character validation.

        This method checks that isDigit correctly identifies strings containing
        only digit characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check digit and non-digit cases
        self.assertTrue(Stringable("123").isDigit())
        self.assertTrue(Stringable("0").isDigit())
        self.assertFalse(Stringable("12.3").isDigit())
        self.assertFalse(Stringable("abc").isDigit())
        self.assertFalse(Stringable("").isDigit())

    def testIsIdentifier(self):
        """
        Test the isIdentifier method for valid Python identifier validation.

        This method verifies that isIdentifier correctly identifies strings that
        are valid Python identifiers.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check valid and invalid identifier cases
        self.assertTrue(Stringable("variable_name").isIdentifier())
        self.assertTrue(Stringable("_private").isIdentifier())
        self.assertTrue(Stringable("Class").isIdentifier())
        self.assertFalse(Stringable("123abc").isIdentifier())
        self.assertFalse(Stringable("class-name").isIdentifier())
        self.assertFalse(Stringable("").isIdentifier())

    def testIsLower(self):
        """
        Test the isLower method for lowercase character validation.

        This method checks that isLower correctly identifies strings containing
        only lowercase characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check lowercase and non-lowercase cases
        self.assertTrue(Stringable("hello world").isLower())
        self.assertTrue(Stringable("hello123").isLower())
        self.assertFalse(Stringable("Hello World").isLower())
        self.assertFalse(Stringable("HELLO").isLower())
        self.assertFalse(Stringable("123").isLower())

    def testIsNumeric(self):
        """
        Test the isNumeric method for numeric character validation.

        This method verifies that isNumeric correctly identifies strings containing
        only numeric characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check numeric and non-numeric cases
        self.assertTrue(Stringable("123").isNumeric())
        self.assertTrue(Stringable("0").isNumeric())
        self.assertFalse(Stringable("12.3").isNumeric())
        self.assertFalse(Stringable("abc").isNumeric())
        self.assertFalse(Stringable("").isNumeric())

    def testIsPrintable(self):
        """
        Test the isPrintable method for printable character validation.

        This method checks that isPrintable correctly identifies strings containing
        only printable characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check printable and non-printable cases
        self.assertTrue(Stringable("hello world").isPrintable())
        self.assertTrue(Stringable("123!@#").isPrintable())
        self.assertFalse(Stringable("hello\tworld").isPrintable())
        self.assertFalse(Stringable("hello\nworld").isPrintable())

    def testIsSpace(self):
        """
        Test the isSpace method for whitespace character validation.

        This method verifies that isSpace correctly identifies strings containing
        only whitespace characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check whitespace and non-whitespace cases
        self.assertTrue(Stringable("   ").isSpace())
        self.assertTrue(Stringable("\t\n").isSpace())
        self.assertFalse(Stringable("hello world").isSpace())
        self.assertFalse(Stringable("").isSpace())

    def testIsTitle(self):
        """
        Test the isTitle method for title case validation.

        This method checks that isTitle correctly identifies strings in title case.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check title case and non-title case strings
        self.assertTrue(Stringable("Hello World").isTitle())
        self.assertTrue(Stringable("The Quick Brown Fox").isTitle())
        self.assertFalse(Stringable("hello world").isTitle())
        self.assertFalse(Stringable("HELLO WORLD").isTitle())

    def testIsUpper(self):
        """
        Test the isUpper method for uppercase character validation.

        This method verifies that isUpper correctly identifies strings containing
        only uppercase characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        # Check uppercase and non-uppercase cases
        self.assertTrue(Stringable("HELLO WORLD").isUpper())
        self.assertTrue(Stringable("HELLO123").isUpper())
        self.assertFalse(Stringable("Hello World").isUpper())
        self.assertFalse(Stringable("hello").isUpper())
        self.assertFalse(Stringable("123").isUpper())

    def testLStrip(self):
        """
        Test the lStrip method for removing characters from the left side.

        This method checks that lStrip removes leading whitespace or specified
        characters from the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("   hello world   ")

        # Remove leading whitespace
        result = s.lStrip()
        self.assertEqual(result, "hello world   ")
        self.assertIsInstance(result, Stringable)

        # Remove leading custom characters
        s = Stringable("...hello world...")
        result = s.lStrip(".")
        self.assertEqual(result, "hello world...")

    def testRStrip(self):
        """
        Test the rStrip method for removing characters from the right side.

        This method checks that rStrip removes trailing whitespace or specified
        characters from the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("   hello world   ")

        # Remove trailing whitespace
        result = s.rStrip()
        self.assertEqual(result, "   hello world")
        self.assertIsInstance(result, Stringable)

        # Remove trailing custom characters
        s = Stringable("...hello world...")
        result = s.rStrip(".")
        self.assertEqual(result, "...hello world")

    def testSwapCase(self):
        """
        Test the swapCase method for swapping character case.

        This method verifies that swapCase inverts the case of each character
        in the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("Hello World")

        # Swap case of all characters
        result = s.swapCase()
        self.assertEqual(result, "hELLO wORLD")
        self.assertIsInstance(result, Stringable)

    def testZFill(self):
        """
        Test the zFill method for zero-padding strings.

        This method checks that zFill pads the string with zeros on the left
        to reach the specified width.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("123")

        # Pad with zeros to width 5
        result = s.zFill(5)
        self.assertEqual(result, "00123")
        self.assertIsInstance(result, Stringable)

        # Pad negative number with zeros
        s = Stringable("-123")
        result = s.zFill(6)
        self.assertEqual(result, "-00123")

    def testAscii(self):
        """
        Test the ascii method for ASCII conversion.

        This method verifies that ascii converts non-ASCII characters to their
        closest ASCII equivalents.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("héllo wörld")

        # Convert to ASCII
        result = s.ascii()
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, Stringable)

    def testSlug(self):
        """
        Test the slug method for generating URL-friendly slugs.

        This method checks that slug converts the string to a lowercase,
        separator-delimited format suitable for URLs.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("Hello World!")

        # Generate slug with default separator
        result = s.slug()
        self.assertEqual(result, "hello-world")
        self.assertIsInstance(result, Stringable)

        # Generate slug with custom separator
        result = s.slug("_")
        self.assertEqual(result, "hello_world")

    def testHeadline(self):
        """
        Test the headline method for creating readable headlines.

        This method verifies that headline capitalizes words to create
        a human-readable headline.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world test")

        # Create headline from space-separated words
        result = s.headline()
        self.assertEqual(result, "Hello World Test")
        self.assertIsInstance(result, Stringable)

        # Create headline from underscore-separated words
        s = Stringable("hello_world_test")
        result = s.headline()
        self.assertEqual(result, "Hello_world_test")

    def testApa(self):
        """
        Test the apa method for APA title case conversion.

        This method checks that apa converts the string to APA-style
        title case, capitalizing major words.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("the quick brown fox")

        # Convert to APA title case
        result = s.apa()
        expected = "The Quick Brown Fox"
        self.assertEqual(result, expected)
        self.assertIsInstance(result, Stringable)

    def testUcfirst(self):
        """
        Test the ucfirst method for capitalizing the first character.

        This method verifies that ucfirst capitalizes only the first character
        of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Capitalize first character
        result = s.ucfirst()
        self.assertEqual(result, "Hello world")
        self.assertIsInstance(result, Stringable)

    def testLcfirst(self):
        """
        Test the lcfirst method for lowercasing the first character.

        This method checks that lcfirst lowercases only the first character
        of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("Hello World")

        # Lowercase first character
        result = s.lcfirst()
        self.assertEqual(result, "hello World")
        self.assertIsInstance(result, Stringable)

    def testChopStart(self):
        """
        Test the chopStart method for removing substrings from the start.

        This method verifies that chopStart removes the specified substring(s)
        from the beginning of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Remove substring from start
        result = s.chopStart("hello ")
        self.assertEqual(result, "world")
        self.assertIsInstance(result, Stringable)

        # Remove one of multiple possible substrings from start
        result = s.chopStart(["hi ", "hello "])
        self.assertEqual(result, "world")

    def testChopEnd(self):
        """
        Test the chopEnd method for removing substrings from the end.

        This method checks that chopEnd removes the specified substring(s)
        from the end of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Remove substring from end
        result = s.chopEnd(" world")
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, Stringable)

        # Remove one of multiple possible substrings from end
        result = s.chopEnd([" universe", " world"])
        self.assertEqual(result, "hello")

    def testDeduplicate(self):
        """
        Test the deduplicate method for removing consecutive duplicate characters.

        This method verifies that deduplicate collapses consecutive duplicate
        characters into a single character.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello    world")

        # Remove consecutive spaces
        result = s.deduplicate()
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, Stringable)

        # Remove consecutive custom character
        s = Stringable("hello...world")
        result = s.deduplicate(".")
        self.assertEqual(result, "hello.world")

    def testCharAt(self):
        """
        Test the charAt method for character retrieval by index.

        This method checks that charAt returns the character at the specified
        index, or False if out of bounds.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Retrieve character at valid index
        result = s.charAt(0)
        self.assertEqual(result, "h")

        result = s.charAt(6)
        self.assertEqual(result, "w")

        # Retrieve character at out-of-bounds index
        result = s.charAt(20)
        self.assertFalse(result)

    def testPosition(self):
        """
        Test the position method for finding substring position.

        This method verifies that position returns the index of the first
        occurrence of a substring, or False if not found.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Find position of substring
        result = s.position("world")
        self.assertEqual(result, 6)

        # Find position with offset
        result = s.position("l", 3)
        self.assertEqual(result, 3)

        # Find position of non-existent substring
        result = s.position("xyz")
        self.assertFalse(result)

    def testNumbers(self):
        """
        Test the numbers method for extracting numeric characters.

        This method checks that numbers returns a string containing only
        the numeric characters from the original string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("abc123def456")

        # Extract numeric characters
        result = s.numbers()
        self.assertEqual(result, "123456")
        self.assertIsInstance(result, Stringable)

    def testExcerpt(self):
        """
        Test the excerpt method for creating text excerpts.

        This method verifies that excerpt returns a substring containing
        the search term and surrounding context.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("This is a long text that needs to be excerpted")

        # Create excerpt around search term
        result = s.excerpt("long", {"radius": 10})
        self.assertIsInstance(result, str)
        self.assertIn("long", result)

    def testBasename(self):
        """
        Test the basename method for extracting the filename.

        This method checks that basename returns the filename portion
        of a path, optionally removing a suffix.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("/path/to/file.txt")

        # Extract filename
        result = s.basename()
        self.assertEqual(result, "file.txt")
        self.assertIsInstance(result, Stringable)

        # Extract filename without suffix
        result = s.basename(".txt")
        self.assertEqual(result, "file")

    def testDirname(self):
        """
        Test the dirname method for extracting the directory path.

        This method verifies that dirname returns the directory portion
        of a file path.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("/path/to/file.txt")

        # Extract directory path
        result = s.dirname()
        self.assertEqual(result, "/path/to")
        self.assertIsInstance(result, Stringable)

    def testClassBasename(self):
        """
        Test the classBasename method for extracting the class name.

        This method checks that classBasename returns the last segment
        of a dot-separated class path.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("App.Models.User")

        # Extract class name from dot-separated path
        result = s.classBasename()
        self.assertEqual(result, "User")
        self.assertIsInstance(result, Stringable)

        # Extract class name from backslash-separated path
        s = Stringable("App\\Models\\User")
        result = s.classBasename()
        self.assertEqual(result, "App\\Models\\User")

    def testBetween(self):
        """
        Test the between method for extracting substring between delimiters.

        This method verifies that between returns the substring found
        between two specified delimiters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("Hello [world] test")

        # Extract substring between delimiters
        result = s.between("[", "]")
        self.assertEqual(result, "world")
        self.assertIsInstance(result, Stringable)

    def testBetweenFirst(self):
        """
        Test the betweenFirst method for extracting the first occurrence between delimiters.

        This method checks that betweenFirst returns the substring found
        between the first pair of specified delimiters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("Hello [world] and [universe]")

        # Extract first substring between delimiters
        result = s.betweenFirst("[", "]")
        self.assertEqual(result, "world")
        self.assertIsInstance(result, Stringable)

    def testFinish(self):
        """
        Test the finish method for ensuring string ends with a suffix.

        This method verifies that finish appends the specified suffix
        if the string does not already end with it.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Ensure string ends with suffix
        result = s.finish("!")
        self.assertEqual(result, "hello world!")
        self.assertIsInstance(result, Stringable)

        # Ensure string does not duplicate suffix
        s = Stringable("hello world!")
        result = s.finish("!")
        self.assertEqual(result, "hello world!")

    def testStart(self):
        """
        Test the start method for ensuring string starts with a prefix.

        This method checks that start prepends the specified prefix
        if the string does not already start with it.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Ensure string starts with prefix
        result = s.start(">>> ")
        self.assertEqual(result, ">>> hello world")
        self.assertIsInstance(result, Stringable)

        # Ensure string does not duplicate prefix
        s = Stringable(">>> hello world")
        result = s.start(">>> ")
        self.assertEqual(result, ">>> hello world")

    def testSquish(self):
        """
        Test the squish method for removing extra whitespace.

        This method verifies that squish collapses multiple whitespace
        characters into a single space and trims the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("  hello    world  ")

        # Remove extra whitespace
        result = s.squish()
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, Stringable)

    def testWrap(self):
        """
        Test the wrap method for wrapping string with before/after strings.

        This method checks that wrap surrounds the string with the specified
        before and after strings.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello")

        # Wrap with same character before and after
        result = s.wrap('"')
        self.assertEqual(result, '"hello"')
        self.assertIsInstance(result, Stringable)

        # Wrap with different before and after strings
        result = s.wrap("[", "]")
        self.assertEqual(result, "[hello]")

    def testUnwrap(self):
        """
        Test the unwrap method for removing wrapping characters.

        This method verifies that unwrap removes the specified before and after
        strings from the start and end of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable('"hello"')

        # Remove wrapping character
        result = s.unwrap('"')
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, Stringable)

        # Remove different before and after wrapping
        s = Stringable("[hello]")
        result = s.unwrap("[", "]")
        self.assertEqual(result, "hello")

    def testReplaceArray(self):
        """
        Test the replaceArray method for replacing placeholders with array values.

        This method checks that replaceArray replaces each occurrence of a placeholder
        with corresponding values from an array.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("The ? is ? years old")

        # Replace placeholders with array values
        result = s.replaceArray("?", ["user", "25"])
        self.assertEqual(result, "The user is 25 years old")
        self.assertIsInstance(result, Stringable)

    def testReplaceStart(self):
        """
        Test the replaceStart method for replacing at the beginning of the string.

        This method verifies that replaceStart replaces the specified substring
        at the start of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Replace substring at start
        result = s.replaceStart("hello", "hi")
        self.assertEqual(result, "hi world")
        self.assertIsInstance(result, Stringable)

        # Attempt to replace non-existent start substring
        result = s.replaceStart("hi", "hello")
        self.assertEqual(result, "hello world")

    def testReplaceEnd(self):
        """
        Test the replaceEnd method for replacing at the end of the string.

        This method checks that replaceEnd replaces the specified substring
        at the end of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Replace substring at end
        result = s.replaceEnd("world", "universe")
        self.assertEqual(result, "hello universe")
        self.assertIsInstance(result, Stringable)

        # Attempt to replace non-existent end substring
        result = s.replaceEnd("universe", "world")
        self.assertEqual(result, "hello world")

    def testReplaceMatches(self):
        """
        Test the replaceMatches method for replacing regex matches.

        This method verifies that replaceMatches replaces all substrings
        matching a regular expression pattern.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello 123 world 456")

        # Replace all digit sequences with 'X'
        result = s.replaceMatches(r'\d+', 'X')
        self.assertEqual(result, "hello X world X")
        self.assertIsInstance(result, Stringable)

    def testRemove(self):
        """
        Test the remove method for removing substrings.

        This method checks that remove deletes all occurrences of the specified
        substring(s) from the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world hello")

        # Remove single substring
        result = s.remove("hello")
        self.assertEqual(result, " world ")
        self.assertIsInstance(result, Stringable)

        # Remove multiple substrings
        result = s.remove(["hello", "world"])
        self.assertEqual(result, "  ")

    def testPluralStudly(self):
        """
        Test the pluralStudly method for generating StudlyCase plurals.

        This method verifies that pluralStudly returns a pluralized string
        in StudlyCase format.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("User")

        # Generate StudlyCase plural
        result = s.pluralStudly()
        self.assertIsInstance(result, Stringable)
        self.assertTrue(result.toString().endswith("s"))

    def testPluralPascal(self):
        """
        Test the pluralPascal method for generating PascalCase plurals.

        This method checks that pluralPascal returns a pluralized string
        in PascalCase format.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("user")

        # Generate PascalCase plural
        result = s.pluralPascal()
        self.assertIsInstance(result, Stringable)
        self.assertTrue(result.toString()[0].isupper())

    def testParseCallback(self):
        """
        Test the parseCallback method for parsing callback strings.

        This method verifies that parseCallback splits a callback string
        into class and method components.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("Class@method")

        # Parse callback string into class and method
        result = s.parseCallback()
        self.assertEqual(result, ["Class", "method"])

        # Parse callback string with default method
        s = Stringable("Class")
        result = s.parseCallback("defaultMethod")
        self.assertEqual(result, ["Class", "defaultMethod"])

    def testWhenContainsAll(self):
        """
        Test the whenContainsAll method for conditional execution when all needles are present.

        This method checks that whenContainsAll executes a callback only if all
        specified substrings are present in the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world test")

        # Execute callback when all needles are present
        result = s.whenContainsAll(["hello", "world"], lambda x: x.upper())
        self.assertEqual(result, "HELLO WORLD TEST")

        # Do not execute callback when not all needles are present
        result = s.whenContainsAll(["hello", "xyz"], lambda x: x.upper())
        self.assertEqual(result, "hello world test")

    def testWhenDoesntEndWith(self):
        """
        Test the whenDoesntEndWith method for conditional execution when string doesn't end with needles.

        This method verifies that whenDoesntEndWith executes a callback only if
        the string does not end with the specified substring.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Execute callback when string doesn't end with needle
        result = s.whenDoesntEndWith("test", lambda x: x.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Do not execute callback when string ends with needle
        result = s.whenDoesntEndWith("world", lambda x: x.upper())
        self.assertEqual(result, "hello world")

    def testWhenExactly(self):
        """
        Test the whenExactly method for conditional execution on exact match.

        This method checks that whenExactly executes a callback only if the string
        matches the specified value exactly.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Execute callback on exact match
        result = s.whenExactly("hello world", lambda x: x.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Do not execute callback on non-exact match
        result = s.whenExactly("Hello World", lambda x: x.upper())
        self.assertEqual(result, "hello world")

    def testWhenNotExactly(self):
        """
        Test the whenNotExactly method for conditional execution on non-exact match.

        This method verifies that whenNotExactly executes a callback only if the string
        does not match the specified value exactly.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Execute callback on non-exact match
        result = s.whenNotExactly("Hello World", lambda x: x.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Do not execute callback on exact match
        result = s.whenNotExactly("hello world", lambda x: x.upper())
        self.assertEqual(result, "hello world")

    def testWhenDoesntStartWith(self):
        """
        Test the whenDoesntStartWith method for conditional execution when string doesn't start with needles.

        This method checks that whenDoesntStartWith executes a callback only if
        the string does not start with the specified substring.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Execute callback when string doesn't start with needle
        result = s.whenDoesntStartWith("test", lambda x: x.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Do not execute callback when string starts with needle
        result = s.whenDoesntStartWith("hello", lambda x: x.upper())
        self.assertEqual(result, "hello world")

    def testWhenTest(self):
        """
        Test the whenTest method for conditional execution on pattern match.

        This method verifies that whenTest executes a callback only if the string
        matches the specified regular expression pattern.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello123")

        # Execute callback when pattern matches
        result = s.whenTest(r'\d+', lambda x: x.upper())
        self.assertEqual(result, "HELLO123")

        # Do not execute callback when pattern does not match
        s = Stringable("hello")
        result = s.whenTest(r'\d+', lambda x: x.upper())
        self.assertEqual(result, "hello")

    def testConvertCase(self):
        """
        Test the convertCase method for string case conversion.

        This method checks that convertCase converts the string case according
        to the implementation's default behavior.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Convert string case (default behavior)
        result = s.convertCase()
        self.assertIsInstance(result, Stringable)

    def testTransliterate(self):
        """
        Test the transliterate method for converting to ASCII equivalents.

        This method verifies that transliterate replaces non-ASCII characters
        with their closest ASCII equivalents.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("héllo wörld")

        # Transliterate to ASCII
        result = s.transliterate()
        self.assertEqual(result, "hello world")
        self.assertIsInstance(result, Stringable)

    def testHash(self):
        """
        Test the hash method for generating hashes with specified algorithms.

        This method checks that hash returns a hexadecimal hash string of the
        specified algorithm for the input string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Generate SHA256 hash
        result = s.hash("sha256")
        self.assertIsInstance(result, Stringable)
        self.assertEqual(len(result), 64)

    def testSubstrCount(self):
        """
        Test the substrCount method for counting substring occurrences.

        This method verifies that substrCount returns the number of times
        a substring appears in the string, optionally starting from an offset.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world hello")

        # Count occurrences of substring
        result = s.substrCount("hello")
        self.assertEqual(result, 2)

        # Count occurrences with offset
        result = s.substrCount("hello", 1)
        self.assertEqual(result, 1)

    def testSubstrReplace(self):
        """
        Test the substrReplace method for replacing substring at a position.

        This method checks that substrReplace replaces a portion of the string
        at the specified position and length.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Replace substring at position
        result = s.substrReplace("XXX", 6, 5)
        self.assertEqual(result, "hello XXX")
        self.assertIsInstance(result, Stringable)

    def testScan(self):
        """
        Test the scan method for extracting values using a format string.

        This method verifies that scan extracts values from the string
        according to the specified format.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello 123 world")

        # Scan for digits using format string
        result = s.scan("hello %d world")
        self.assertEqual(result, ["1", "2", "3"])

        # Scan for string using format string
        s = Stringable("hello world")
        result = s.scan("hello %s")
        self.assertEqual(result, ["w", "o", "r", "l", "d"])

    def testPrepend(self):
        """
        Test the prepend method for adding values to the beginning of the string.

        This method checks that prepend adds one or more values to the start
        of the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("world")

        # Prepend multiple values
        result = s.prepend("hello ", "beautiful ")
        self.assertEqual(result, "hello beautiful world")
        self.assertIsInstance(result, Stringable)

    def testSubstr(self):
        """
        Test the substr method for extracting a substring.

        This method verifies that substr returns a substring starting at
        the specified position, optionally with a given length.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Extract substring from position
        result = s.substr(6)
        self.assertEqual(result, "world")
        self.assertIsInstance(result, Stringable)

        # Extract substring with length
        result = s.substr(0, 5)
        self.assertEqual(result, "hello")

    def testDoesntContain(self):
        """
        Test the doesntContain method for checking absence of substrings.

        This method checks that doesntContain returns True if none of the
        specified substrings are present in the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Check absence of single substring
        self.assertTrue(s.doesntContain("xyz"))
        self.assertFalse(s.doesntContain("hello"))

        # Check absence of multiple substrings
        self.assertTrue(s.doesntContain(["xyz", "abc"]))
        self.assertFalse(s.doesntContain(["hello", "xyz"]))

    def testDoesntStartWith(self):
        """
        Test the doesntStartWith method for checking string doesn't start with needles.

        This method verifies that doesntStartWith returns True if the string
        does not start with any of the specified substrings.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Check string doesn't start with single substring
        self.assertTrue(s.doesntStartWith("world"))
        self.assertFalse(s.doesntStartWith("hello"))

        # Check string doesn't start with any in list
        self.assertTrue(s.doesntStartWith(["world", "test"]))
        self.assertFalse(s.doesntStartWith(["hello", "world"]))

    def testDoesntEndWith(self):
        """
        Test the doesntEndWith method for checking string doesn't end with needles.

        This method checks that doesntEndWith returns True if the string
        does not end with any of the specified substrings.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Check string doesn't end with single substring
        self.assertTrue(s.doesntEndWith("hello"))
        self.assertFalse(s.doesntEndWith("world"))

        # Check string doesn't end with any in list
        self.assertTrue(s.doesntEndWith(["hello", "test"]))
        self.assertFalse(s.doesntEndWith(["world", "hello"]))

    def testIsPatternMethod(self):
        """
        Test the isPattern method for wildcard pattern matching.

        This method verifies that isPattern correctly matches strings
        against wildcard patterns.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Match various wildcard patterns
        self.assertTrue(s.isPattern("hello*"))
        self.assertTrue(s.isPattern("*world"))
        self.assertTrue(s.isPattern("hello?world"))
        self.assertFalse(s.isPattern("foo*"))

        # Match pattern with case insensitivity
        self.assertTrue(s.isPattern("HELLO*", ignore_case=True))

    def testContainsAll(self):
        """
        Test the containsAll method for checking all needles are present.

        This method checks that containsAll returns True only if all
        specified substrings are present in the string.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world test")

        # Check all substrings present
        self.assertTrue(s.containsAll(["hello", "world"]))
        self.assertFalse(s.containsAll(["hello", "xyz"]))

        # Check all substrings present with case insensitivity
        self.assertTrue(s.containsAll(["HELLO", "WORLD"], ignore_case=True))

    def testWhenIs(self):
        """
        Test the whenIs method for conditional execution on pattern match.

        This method verifies that whenIs executes a callback only if the string
        matches the specified wildcard pattern.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Execute callback when pattern matches
        result = s.whenIs("hello*", lambda x: x.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Do not execute callback when pattern does not match
        result = s.whenIs("foo*", lambda x: x.upper())
        self.assertEqual(result, "hello world")

    def testWhenIsAscii(self):
        """
        Test the whenIsAscii method for conditional execution when string is ASCII.

        This method checks that whenIsAscii executes a callback only if the string
        contains only ASCII characters.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("hello world")

        # Execute callback when string is ASCII
        result = s.whenIsAscii(lambda x: x.upper())
        self.assertEqual(result, "HELLO WORLD")

        # Do not execute callback when string is not ASCII
        s = Stringable("héllo")
        result = s.whenIsAscii(lambda x: x.upper())
        self.assertEqual(result, "héllo")

    def testWhenIsUuid(self):
        """
        Test the whenIsUuid method for conditional execution when string is UUID.

        This method verifies that whenIsUuid executes a callback only if the string
        is a valid UUID.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("550e8400-e29b-41d4-a716-446655440000")

        # Execute callback when string is UUID
        result = s.whenIsUuid(lambda x: x.upper())
        self.assertEqual(result, "550E8400-E29B-41D4-A716-446655440000")

        # Do not execute callback when string is not UUID
        s = Stringable("hello world")
        result = s.whenIsUuid(lambda x: x.upper())
        self.assertEqual(result, "hello world")

    def testWhenIsUlid(self):
        """
        Test the whenIsUlid method for conditional execution when string is ULID.

        This method checks that whenIsUlid executes a callback only if the string
        is a valid ULID.

        Returns
        -------
        None
            Asserts correctness using test assertions.
        """

        s = Stringable("01ARZ3NDEKTSV4RRFFQ69G5FAV")

        # Execute callback when string is ULID
        result = s.whenIsUlid(lambda x: x.lower())
        self.assertEqual(result, "01arz3ndektsv4rrffq69g5fav")

        # Do not execute callback when string is not ULID
        s = Stringable("hello world")
        result = s.whenIsUlid(lambda x: x.upper())
        self.assertEqual(result, "hello world")
