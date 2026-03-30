from __future__ import annotations
from orionis.test import TestCase
from orionis.services.environment.validators.key_name import ValidateKeyName

# ---------------------------------------------------------------------------
# TestValidateKeyNameValid
# ---------------------------------------------------------------------------

class TestValidateKeyNameValid(TestCase):

    def testSingleUppercaseLetter(self):
        """
        Accept a single uppercase letter as a valid key name.

        Validates that the minimum-length valid name (one letter) passes
        the regex pattern without raising any exception.
        """
        self.assertEqual(ValidateKeyName("A"), "A")

    def testAllUppercaseLetters(self):
        """
        Accept a name composed entirely of uppercase letters.

        Validates that a typical environment variable name such as 'HELLO'
        passes validation and is returned unchanged.
        """
        self.assertEqual(ValidateKeyName("HELLO"), "HELLO")

    def testUppercaseWithUnderscore(self):
        """
        Accept a name that contains uppercase letters and underscores.

        Validates the most common environment variable naming convention
        such as 'MY_VAR' is correctly accepted.
        """
        self.assertEqual(ValidateKeyName("MY_VAR"), "MY_VAR")

    def testUppercaseWithTrailingDigits(self):
        """
        Accept a name that ends with numeric digits.

        Confirms that digits are allowed after the initial uppercase letter,
        which is a common pattern such as 'VAR123'.
        """
        self.assertEqual(ValidateKeyName("VAR123"), "VAR123")

    def testUppercaseWithInterspersedDigits(self):
        """
        Accept a name with digits and underscores interspersed.

        Validates that complex but valid names like 'A1_B2_C3' pass the
        pattern check without error.
        """
        self.assertEqual(ValidateKeyName("A1_B2_C3"), "A1_B2_C3")

    def testMultipleConsecutiveUnderscores(self):
        """
        Accept a name containing multiple consecutive underscores.

        Confirms that the pattern does not restrict the count or placement
        of underscores beyond requiring the first character to be uppercase.
        """
        self.assertEqual(ValidateKeyName("A__B"), "A__B")

    def testLongValidName(self):
        """
        Accept a long name composed of valid characters.

        Validates that there is no implicit length restriction by testing a
        name with many characters.
        """
        self.assertEqual(
            ValidateKeyName("DATABASE_CONNECTION_POOL_SIZE"),
            "DATABASE_CONNECTION_POOL_SIZE",
        )

    def testReturnsExactSameString(self):
        """
        Return the exact string object passed as the key.

        Confirms that the validator does not mutate or copy the input
        string, preserving original identity where applicable.
        """
        key = "MY_KEY"
        result = ValidateKeyName(key)
        self.assertEqual(result, key)

# ---------------------------------------------------------------------------
# TestValidateKeyNameTypeError
# ---------------------------------------------------------------------------

class TestValidateKeyNameTypeError(TestCase):

    def testRaisesTypeErrorForInteger(self):
        """
        Raise TypeError when an integer is passed as the key.

        Validates that non-string inputs trigger a TypeError with a message
        that reports the actual received type.
        """
        with self.assertRaises(TypeError):
            ValidateKeyName(42)

    def testRaisesTypeErrorForFloat(self):
        """
        Raise TypeError when a float is passed as the key.

        Validates that floating-point values are rejected as non-string
        inputs.
        """
        with self.assertRaises(TypeError):
            ValidateKeyName(3.14)

    def testRaisesTypeErrorForNone(self):
        """
        Raise TypeError when None is passed as the key.

        Confirms that None is treated as a non-string and rejected before
        the pattern check is reached.
        """
        with self.assertRaises(TypeError):
            ValidateKeyName(None)

    def testRaisesTypeErrorForList(self):
        """
        Raise TypeError when a list is passed as the key.

        Validates that iterable non-string types are not accepted as
        environment variable names.
        """
        with self.assertRaises(TypeError):
            ValidateKeyName(["MY_KEY"])

    def testRaisesTypeErrorForBool(self):
        """
        Raise TypeError when a boolean is passed as the key.

        Confirms that booleans (which are int subclasses in Python) are
        still rejected because they are not strings.
        """
        with self.assertRaises(TypeError):
            ValidateKeyName(True)

    def testErrorMessageContainsTypeName(self):
        """
        Include the received type name in the TypeError message.

        Validates that the error message is actionable and clearly reports
        the unexpected type so callers can diagnose the problem.
        """
        try:
            ValidateKeyName(99)
            self.fail("Expected TypeError was not raised")
        except TypeError as exc:
            self.assertIn("int", str(exc))

# ---------------------------------------------------------------------------
# TestValidateKeyNameValueError
# ---------------------------------------------------------------------------

class TestValidateKeyNameValueError(TestCase):

    def testRaisesValueErrorForEmptyString(self):
        """
        Raise ValueError when an empty string is provided.

        Validates that an empty key fails the regex pattern because it does
        not start with an uppercase letter.
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("")

    def testRaisesValueErrorForLowercaseName(self):
        """
        Raise ValueError when the key contains only lowercase letters.

        Confirms that 'myvar' fails because it does not start with an
        uppercase letter.
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("myvar")

    def testRaisesValueErrorForMixedCase(self):
        """
        Raise ValueError when the key mixes uppercase and lowercase.

        Validates that 'MyVar' is rejected because lowercase letters are
        not allowed anywhere in a valid key name.
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("MyVar")

    def testRaisesValueErrorForLeadingDigit(self):
        """
        Raise ValueError when the key starts with a numeric digit.

        Confirms that '1VAR' fails the pattern which requires the first
        character to be an uppercase letter.
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("1VAR")

    def testRaisesValueErrorForLeadingUnderscore(self):
        """
        Raise ValueError when the key starts with an underscore.

        Validates that '_VAR' is rejected because the first character must
        be an uppercase letter, not an underscore.
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("_VAR")

    def testRaisesValueErrorForHyphen(self):
        """
        Raise ValueError when the key contains a hyphen character.

        Validates that 'MY-VAR' is rejected because hyphens are not in the
        set of allowed characters (uppercase, digits, underscores).
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("MY-VAR")

    def testRaisesValueErrorForSpaces(self):
        """
        Raise ValueError when the key contains a space character.

        Confirms that 'MY VAR' fails because spaces are not allowed in
        environment variable names.
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("MY VAR")

    def testRaisesValueErrorForDotCharacter(self):
        """
        Raise ValueError when the key contains a period character.

        Validates that 'MY.VAR' is rejected because dots are not part of
        the allowed character set.
        """
        with self.assertRaises(ValueError):
            ValidateKeyName("MY.VAR")

    def testErrorMessageContainsKeyName(self):
        """
        Include the invalid key name in the ValueError message.

        Ensures the error message gives the caller enough context to
        identify which key caused the validation failure.
        """
        bad_key = "bad_key"
        try:
            ValidateKeyName(bad_key)
            self.fail("Expected ValueError was not raised")
        except ValueError as exc:
            self.assertIn(bad_key, str(exc))
