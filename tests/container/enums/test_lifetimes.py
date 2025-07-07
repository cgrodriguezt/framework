from orionis.container.enums.lifetimes import Lifetime
from orionis.test.cases.asynchronous import AsyncTestCase

class TestLifetime(AsyncTestCase):
    """
    Test cases for the Lifetime enum in orionis.container.enums.lifetimes.

    Notes
    -----
    This test suite validates the enumeration values and behavior of the Lifetime enum
    which defines the lifecycle types for dependency injection.
    """

    async def testLifetimeValuesExist(self) -> None:
        """
        Test that the Lifetime enum contains the expected values.

        Verifies that TRANSIENT, SINGLETON, and SCOPED values are present in the enum.
        """
        self.assertIn(Lifetime.TRANSIENT, Lifetime)
        self.assertIn(Lifetime.SINGLETON, Lifetime)
        self.assertIn(Lifetime.SCOPED, Lifetime)

    async def testLifetimeValuesAreUnique(self) -> None:
        """
        Test that all Lifetime enum values are unique.

        Ensures that each enum value has a distinct integer value.
        """
        values = [member.value for member in Lifetime]
        self.assertEqual(len(values), len(set(values)))

    async def testLifetimeCount(self) -> None:
        """
        Test that the Lifetime enum has exactly 3 members.

        Verifies that no additional or missing lifecycle types exist.
        """
        self.assertEqual(len(list(Lifetime)), 3)

    async def testLifetimeStringRepresentation(self) -> None:
        """
        Test the string representation of Lifetime enum values.

        Verifies that the string representation of enum values matches their names.
        """
        self.assertEqual(str(Lifetime.TRANSIENT), "Lifetime.TRANSIENT")
        self.assertEqual(str(Lifetime.SINGLETON), "Lifetime.SINGLETON")
        self.assertEqual(str(Lifetime.SCOPED), "Lifetime.SCOPED")

    async def testLifetimeComparison(self) -> None:
        """
        Test comparison operations between Lifetime enum values.

        Verifies that enum values can be correctly compared with each other.
        """
        self.assertNotEqual(Lifetime.TRANSIENT, Lifetime.SINGLETON)
        self.assertNotEqual(Lifetime.SINGLETON, Lifetime.SCOPED)
        self.assertNotEqual(Lifetime.TRANSIENT, Lifetime.SCOPED)

        self.assertEqual(Lifetime.TRANSIENT, Lifetime.TRANSIENT)
        self.assertEqual(Lifetime.SINGLETON, Lifetime.SINGLETON)
        self.assertEqual(Lifetime.SCOPED, Lifetime.SCOPED)