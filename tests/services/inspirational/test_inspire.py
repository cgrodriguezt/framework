from typing import Dict, List
from unittest.mock import patch
from orionis.services.inspirational.inspire import Inspire
from orionis.services.inspirational.quotes import INSPIRATIONAL_QUOTES
from orionis.test.cases.synchronous import SyncTestCase


class TestInspire(SyncTestCase):
    """
    Test suite for the Inspire service class.

    This class contains comprehensive tests for the Inspire service,
    covering initialization scenarios, quote selection functionality,
    validation mechanisms, and edge cases. The tests ensure proper
    behavior of the inspirational quote service under various conditions.
    """

    def testInitWithDefaultQuotes(self) -> None:
        """
        Test initialization with default quotes.

        Verifies that when no quotes are provided during initialization,
        the service correctly uses the default INSPIRATIONAL_QUOTES list
        and that the internal state is properly set up.

        Raises
        ------
        AssertionError
            If the initialization doesn't use default quotes correctly
            or if the quote structure is invalid.
        """
        inspire = Inspire()
        quote = inspire.random()

        self.assertIsInstance(quote, dict)
        self.assertIn('quote', quote)
        self.assertIn('author', quote)
        self.assertIsInstance(quote['quote'], str)
        self.assertIsInstance(quote['author'], str)
        self.assertGreater(len(quote['quote']), 0)
        self.assertGreater(len(quote['author']), 0)

    def testInitWithNoneQuotes(self) -> None:
        """
        Test initialization with None as quotes parameter.

        Verifies that passing None explicitly to the constructor
        results in the service using the default quotes list,
        ensuring backwards compatibility and proper null handling.

        Raises
        ------
        AssertionError
            If None parameter doesn't trigger default quotes usage
            or if the resulting service state is invalid.
        """
        inspire = Inspire(quotes=None)
        quote = inspire.random()

        self.assertIsInstance(quote, dict)
        self.assertIn('quote', quote)
        self.assertIn('author', quote)

    def testInitWithEmptyList(self) -> None:
        """
        Test initialization with empty quotes list.

        Verifies that providing an empty list as quotes parameter
        results in the service using the default quotes list,
        ensuring graceful handling of edge cases.

        Raises
        ------
        AssertionError
            If empty list doesn't trigger default quotes usage
            or if the fallback mechanism fails.
        """
        inspire = Inspire(quotes=[])
        quote = inspire.random()

        self.assertIsInstance(quote, dict)
        self.assertIn('quote', quote)
        self.assertIn('author', quote)

    def testInitWithValidCustomQuotes(self) -> None:
        """
        Test initialization with valid custom quotes.

        Verifies that providing a properly formatted list of custom quotes
        results in the service using those quotes instead of the defaults,
        and that quote selection works correctly with custom data.

        Raises
        ------
        AssertionError
            If custom quotes are not properly stored or used,
            or if the quote structure validation fails.
        """
        custom_quotes = [
            {"quote": "Test quote 1", "author": "Test Author 1"},
            {"quote": "Test quote 2", "author": "Test Author 2"}
        ]
        inspire = Inspire(quotes=custom_quotes)
        quote = inspire.random()

        self.assertIsInstance(quote, dict)
        self.assertIn('quote', quote)
        self.assertIn('author', quote)
        self.assertIn(quote['quote'], ["Test quote 1", "Test quote 2"])
        self.assertIn(quote['author'], ["Test Author 1", "Test Author 2"])

    def testInitWithInvalidQuoteStructureNonDict(self) -> None:
        """
        Test initialization with invalid quote structure (non-dictionary).

        Verifies that providing quotes that are not dictionaries
        raises a ValueError with an appropriate error message,
        ensuring input validation works correctly.

        Raises
        ------
        AssertionError
            If ValueError is not raised for invalid quote structure
            or if the error message is incorrect.
        """
        invalid_quotes = ["not a dict", {"quote": "valid", "author": "valid"}]

        with self.assertRaises(ValueError) as context:
            Inspire(quotes=invalid_quotes)

        self.assertEqual(
            str(context.exception),
            "Quotes must be provided as a list of dictionaries."
        )

    def testInitWithInvalidQuoteStructureMissingQuoteKey(self) -> None:
        """
        Test initialization with missing 'quote' key in dictionary.

        Verifies that providing dictionaries without the required 'quote'
        key raises a ValueError with an appropriate error message,
        ensuring structural validation works correctly.

        Raises
        ------
        AssertionError
            If ValueError is not raised for missing 'quote' key
            or if the error message is incorrect.
        """
        invalid_quotes = [
            {"author": "Test Author", "content": "Missing quote key"}
        ]

        with self.assertRaises(ValueError) as context:
            Inspire(quotes=invalid_quotes)

        self.assertEqual(
            str(context.exception),
            "Each quote dictionary must contain 'quote' and 'author' keys."
        )

    def testInitWithInvalidQuoteStructureMissingAuthorKey(self) -> None:
        """
        Test initialization with missing 'author' key in dictionary.

        Verifies that providing dictionaries without the required 'author'
        key raises a ValueError with an appropriate error message,
        ensuring structural validation works correctly.

        Raises
        ------
        AssertionError
            If ValueError is not raised for missing 'author' key
            or if the error message is incorrect.
        """
        invalid_quotes = [
            {"quote": "Test quote", "writer": "Missing author key"}
        ]

        with self.assertRaises(ValueError) as context:
            Inspire(quotes=invalid_quotes)

        self.assertEqual(
            str(context.exception),
            "Each quote dictionary must contain 'quote' and 'author' keys."
        )

    def testInitWithMixedValidAndInvalidQuotes(self) -> None:
        """
        Test initialization with mixed valid and invalid quotes.

        Verifies that if any quote in the list is invalid, the entire
        initialization fails with a ValueError, ensuring strict validation
        of all provided data.

        Raises
        ------
        AssertionError
            If ValueError is not raised when mixed valid/invalid quotes
            are provided, or if validation is not comprehensive.
        """
        mixed_quotes = [
            {"quote": "Valid quote", "author": "Valid Author"},
            {"quote": "Missing author key"}
        ]

        with self.assertRaises(ValueError) as context:
            Inspire(quotes=mixed_quotes)

        self.assertEqual(
            str(context.exception),
            "Each quote dictionary must contain 'quote' and 'author' keys."
        )

    def testRandomReturnsValidStructure(self) -> None:
        """
        Test that random method returns valid quote structure.

        Verifies that the random method consistently returns a dictionary
        with the correct structure containing 'quote' and 'author' keys
        with string values, ensuring API contract compliance.

        Raises
        ------
        AssertionError
            If the returned structure is invalid or doesn't meet
            the expected format requirements.
        """
        inspire = Inspire()

        for _ in range(10):  # Test multiple calls for consistency
            quote = inspire.random()

            self.assertIsInstance(quote, dict)
            self.assertIn('quote', quote)
            self.assertIn('author', quote)
            self.assertIsInstance(quote['quote'], str)
            self.assertIsInstance(quote['author'], str)
            self.assertGreater(len(quote['quote']), 0)
            self.assertGreater(len(quote['author']), 0)

    def testRandomWithSingleQuote(self) -> None:
        """
        Test random method behavior with single quote.

        Verifies that when only one quote is available, the random method
        consistently returns that same quote, ensuring deterministic
        behavior in edge cases.

        Raises
        ------
        AssertionError
            If the single quote is not returned consistently
            or if the structure is invalid.
        """
        single_quote = [{"quote": "Only quote", "author": "Only Author"}]
        inspire = Inspire(quotes=single_quote)

        for _ in range(5):  # Test multiple calls for consistency
            quote = inspire.random()
            self.assertEqual(quote['quote'], "Only quote")
            self.assertEqual(quote['author'], "Only Author")

    @patch('random.randint')
    def testRandomSelectionDistribution(self, mock_randint) -> None:
        """
        Test random selection uses proper index distribution.

        Verifies that the random method uses random.randint with correct
        parameters (0 to len-1) and properly selects quotes based on
        the generated index, ensuring proper randomization logic.

        Parameters
        ----------
        mock_randint : unittest.mock.MagicMock
            Mocked random.randint function for controlled testing.

        Raises
        ------
        AssertionError
            If random.randint is not called with correct parameters
            or if quote selection logic is incorrect.
        """
        custom_quotes = [
            {"quote": "First quote", "author": "First Author"},
            {"quote": "Second quote", "author": "Second Author"},
            {"quote": "Third quote", "author": "Third Author"}
        ]
        inspire = Inspire(quotes=custom_quotes)

        # Test selection of first quote (index 0)
        mock_randint.return_value = 0
        quote = inspire.random()
        mock_randint.assert_called_with(0, 2)  # 0 to len-1
        self.assertEqual(quote['quote'], "First quote")
        self.assertEqual(quote['author'], "First Author")

        # Test selection of last quote (index 2)
        mock_randint.return_value = 2
        quote = inspire.random()
        mock_randint.assert_called_with(0, 2)
        self.assertEqual(quote['quote'], "Third quote")
        self.assertEqual(quote['author'], "Third Author")

    @patch('random.randint')
    def testRandomWithNoneValueInList(self, mock_randint) -> None:
        """
        Test random method behavior when None value is selected from internal list.

        Verifies that when the random selection results in a None value
        that somehow gets into the internal quotes list (edge case scenario),
        the fallback method is properly invoked and returns the expected
        fallback quote.

        Parameters
        ----------
        mock_randint : unittest.mock.MagicMock
            Mocked random.randint function for controlled testing.

        Raises
        ------
        AssertionError
            If fallback mechanism doesn't work correctly when None
            is encountered, or if fallback quote is incorrect.
        """
        # Create a valid inspire instance first
        valid_quotes = [
            {"quote": "Valid quote", "author": "Valid Author"},
            {"quote": "Another quote", "author": "Another Author"}
        ]
        inspire = Inspire(quotes=valid_quotes)

        # Manually inject None into the internal quotes list to simulate edge case
        # This bypasses the validation that normally prevents None values
        inspire._Inspire__quotes[1] = None

        # Force selection of None value
        mock_randint.return_value = 1
        quote = inspire.random()

        # Should return fallback quote
        self.assertEqual(
            quote['quote'],
            'Greatness is not measured by what you build, but by what you inspire others to create.'
        )
        self.assertEqual(quote['author'], 'Raul M. Uñate')

    def testFallbackQuoteStructure(self) -> None:
        """
        Test fallback quote structure and content.

        Verifies that the fallback mechanism returns a quote with the
        correct structure and expected content when no quotes are available
        or when fallback conditions are met.

        Raises
        ------
        AssertionError
            If fallback quote structure is invalid or content
            doesn't match expected values.
        """
        # Test fallback by creating service with empty list that gets converted to default
        # but then mock the length to be 0
        inspire = Inspire()

        # Access the private fallback method through testing
        with patch.object(inspire, f'_{inspire.__class__.__name__}__quotes', []):
            quote = inspire.random()

            self.assertIsInstance(quote, dict)
            self.assertIn('quote', quote)
            self.assertIn('author', quote)
            self.assertEqual(
                quote['quote'],
                'Greatness is not measured by what you build, but by what you inspire others to create.'
            )
            self.assertEqual(quote['author'], 'Raul M. Uñate')

    def testDefaultQuotesIntegrity(self) -> None:
        """
        Test integrity of default INSPIRATIONAL_QUOTES data.

        Verifies that the default quotes list contains valid data
        structures and that all quotes have the required format,
        ensuring data integrity of the default dataset.

        Raises
        ------
        AssertionError
            If any quote in the default list has invalid structure
            or if the list is empty or malformed.
        """
        self.assertIsInstance(INSPIRATIONAL_QUOTES, list)
        self.assertGreater(len(INSPIRATIONAL_QUOTES), 0)

        for quote in INSPIRATIONAL_QUOTES:
            self.assertIsInstance(quote, dict)
            self.assertIn('quote', quote)
            self.assertIn('author', quote)
            self.assertIsInstance(quote['quote'], str)
            self.assertIsInstance(quote['author'], str)
            self.assertGreater(len(quote['quote']), 0)
            self.assertGreater(len(quote['author']), 0)

    def testRandomnessDistribution(self) -> None:
        """
        Test randomness distribution over multiple calls.

        Verifies that the random method produces varied results over
        multiple calls when multiple quotes are available, ensuring
        the randomization mechanism works effectively.

        Raises
        ------
        AssertionError
            If randomness distribution is poor or if the same quote
            is returned too frequently, indicating randomization issues.
        """
        custom_quotes = [
            {"quote": f"Quote {i}", "author": f"Author {i}"}
            for i in range(10)
        ]
        inspire = Inspire(quotes=custom_quotes)

        # Collect results from multiple calls
        results = []
        for _ in range(50):
            quote = inspire.random()
            results.append(quote['quote'])

        # Check that we got some variety (at least 3 different quotes in 50 calls)
        unique_quotes = set(results)
        self.assertGreaterEqual(len(unique_quotes), 3)

    def testMethodReturnTypes(self) -> None:
        """
        Test that all public methods return expected types.

        Verifies that the random method consistently returns the correct
        data type (dictionary) and that the return value structure
        matches the expected interface contract.

        Raises
        ------
        AssertionError
            If return types don't match expected types or if
            the interface contract is violated.
        """
        inspire = Inspire()
        quote = inspire.random()

        # Test return type
        self.assertIsInstance(quote, dict, "random() should return a dictionary")

        # Test dictionary structure
        self.assertEqual(len(quote), 2, "Quote dictionary should have exactly 2 keys")
        self.assertIn('quote', quote, "Dictionary should contain 'quote' key")
        self.assertIn('author', quote, "Dictionary should contain 'author' key")

        # Test value types
        self.assertIsInstance(quote['quote'], str, "'quote' value should be a string")
        self.assertIsInstance(quote['author'], str, "'author' value should be a string")