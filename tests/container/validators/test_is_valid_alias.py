from orionis.container.validators.is_valid_alias import IsValidAlias
from orionis.container.exceptions.type import OrionisContainerTypeError
from orionis.test.cases.test_case import TestCase

class TestIsValidAlias(TestCase):
    """
    Test cases for the IsValidAlias validator in orionis.container.validators.is_valid_alias.

    Notes
    -----
    This test suite validates the functionality of the IsValidAlias validator
    which ensures that alias values are valid strings without invalid characters.
    """

    async def testValidAliases(self) -> None:
        """
        Test that validation passes when valid aliases are provided.
        """
        valid_aliases = [
            "valid",
            "valid_alias",
            "validAlias",
            "valid123",
            "valid_123",
            "v",
            "1",
            "_",
            "valid_alias_with_underscores",
            "ValidAliasWithMixedCase",
            "VALID_UPPERCASE_ALIAS"
        ]

        for alias in valid_aliases:
            IsValidAlias(alias)

    async def testInvalidAliasTypes(self) -> None:
        """
        Test that validation fails when non-string types are provided.
        """
        invalid_types = [
            123,
            3.14,
            None,
            True,
            False,
            [],
            {},
            (),
            set()
        ]

        for value in invalid_types:
            with self.assertRaises(OrionisContainerTypeError) as context:
                IsValidAlias(value)

    async def testAliasWithInvalidCharacters(self) -> None:
        """
        Test that validation fails when aliases contain invalid characters.
        """
        invalid_aliases = [
            "invalid alias",  # space
            "invalid\talias",  # tab
            "invalid\nalias",  # newline
            "invalid@alias",   # special character
            "invalid#alias",   # special character
            "invalid$alias",   # special character
            "invalid%alias",   # special character
            "invalid&alias",   # special character
            "invalid*alias",   # special character
            "invalid(alias)",  # parentheses
            "invalid[alias]",  # brackets
            "invalid{alias}",  # braces
            "invalid;alias",   # semicolon
            "invalid:alias",   # colon
            "invalid,alias",   # comma
            "invalid/alias",   # slash
            "invalid\\alias",  # backslash
            "invalid<alias>",  # angle brackets
            "invalid|alias",   # pipe
            "invalid`alias",   # backtick
            'invalid"alias',   # double quote
            "invalid'alias"    # single quote
        ]

        for alias in invalid_aliases:
            with self.assertRaises(OrionisContainerTypeError) as context:
                IsValidAlias(alias)

            expected_msg_start = f"Alias '{alias}' contains invalid characters."
            self.assertTrue(str(context.exception).startswith(expected_msg_start))
            self.assertIn("Aliases must not contain whitespace or special symbols", str(context.exception))

    async def testEmptyAlias(self) -> None:
        """
        Test that validation fails with an empty string.
        """
        # Empty string should be rejected
        with self.assertRaises(OrionisContainerTypeError) as context:
            IsValidAlias("")

        self.assertEqual(
            str(context.exception),
            "Alias cannot be None, empty, or whitespace only."
        )

        # Whitespace-only string should also be rejected
        with self.assertRaises(OrionisContainerTypeError) as context:
            IsValidAlias("   ")

        self.assertEqual(
            str(context.exception),
            "Alias cannot be None, empty, or whitespace only."
        )