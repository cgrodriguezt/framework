from orionis.container.validators.lifetime import LifetimeValidator
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions.type import OrionisContainerTypeError
from orionis.test.cases.case import TestCase

class TestLifetimeValidator(TestCase):
    """
    Test cases for the LifetimeValidator in orionis.container.validators.lifetime.

    Notes
    -----
    This test suite validates the functionality of the LifetimeValidator
    which ensures that lifetime values are correctly validated and converted.
    """

    async def testValidLifetimeEnumValues(self) -> None:
        """
        Test that validation passes when Lifetime enum values are provided.
        """
        self.assertEqual(LifetimeValidator(Lifetime.TRANSIENT), Lifetime.TRANSIENT)
        self.assertEqual(LifetimeValidator(Lifetime.SINGLETON), Lifetime.SINGLETON)
        self.assertEqual(LifetimeValidator(Lifetime.SCOPED), Lifetime.SCOPED)

    async def testValidLifetimeStringValues(self) -> None:
        """
        Test that validation passes when valid string representations are provided.
        """
        self.assertEqual(LifetimeValidator("TRANSIENT"), Lifetime.TRANSIENT)
        self.assertEqual(LifetimeValidator("SINGLETON"), Lifetime.SINGLETON)
        self.assertEqual(LifetimeValidator("SCOPED"), Lifetime.SCOPED)

        # Test with lowercase and mixed case
        self.assertEqual(LifetimeValidator("transient"), Lifetime.TRANSIENT)
        self.assertEqual(LifetimeValidator("Singleton"), Lifetime.SINGLETON)
        self.assertEqual(LifetimeValidator("scoped"), Lifetime.SCOPED)

        # Test with extra whitespace
        self.assertEqual(LifetimeValidator(" TRANSIENT "), Lifetime.TRANSIENT)
        self.assertEqual(LifetimeValidator("  singleton  "), Lifetime.SINGLETON)

    async def testInvalidLifetimeStringValue(self) -> None:
        """
        Test that validation fails when invalid string representations are provided.
        """
        with self.assertRaises(OrionisContainerTypeError) as context:
            LifetimeValidator("INVALID_LIFETIME")

        self.assertIn("Invalid lifetime 'INVALID_LIFETIME'", str(context.exception))
        self.assertIn("Valid options are:", str(context.exception))
        self.assertIn("TRANSIENT", str(context.exception))
        self.assertIn("SINGLETON", str(context.exception))
        self.assertIn("SCOPED", str(context.exception))

    async def testInvalidLifetimeType(self) -> None:
        """
        Test that validation fails when invalid types are provided.
        """
        invalid_values = [
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

        for value in invalid_values:
            with self.assertRaises(OrionisContainerTypeError) as context:
                LifetimeValidator(value)

            expected_msg = f"Lifetime must be of type str or Lifetime enum, got {type(value).__name__}."
            self.assertEqual(str(context.exception), expected_msg)