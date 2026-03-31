from __future__ import annotations
from dataclasses import FrozenInstanceError
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.dependencies.entities.signature import Signature
from orionis.test import TestCase

def _make_argument(name: str = "dep", resolved: bool = True) -> Argument:
    """Create a minimal resolved Argument."""
    return Argument(
        name=name,
        resolved=resolved,
        module_name="orionis.services.cache",
        class_name="FileBasedCache",
        type=object,
        full_class_path="orionis.services.cache.FileBasedCache",
    )

def _make_signature(
    resolved: dict | None = None,
    unresolved: dict | None = None,
    ordered: dict | None = None,
) -> Signature:
    """Create a Signature instance with sensible defaults."""
    return Signature(
        resolved=resolved if resolved is not None else {},
        unresolved=unresolved if unresolved is not None else {},
        ordered=ordered if ordered is not None else {},
    )

# ===========================================================================
# TestSignature
# ===========================================================================

class TestSignature(TestCase):

    def testCanBeInstantiatedWithEmptyDicts(self) -> None:
        """
        Assert that Signature can be created with empty dicts.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = _make_signature()
        self.assertIsInstance(sig, Signature)

    def testResolvedFieldIsPersisted(self) -> None:
        """
        Assert that the resolved dict is stored correctly.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument()
        sig = _make_signature(resolved={"dep": arg})
        self.assertIn("dep", sig.resolved)

    def testUnresolvedFieldIsPersisted(self) -> None:
        """
        Assert that the unresolved dict is stored correctly.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument("missing", resolved=False)
        sig = _make_signature(unresolved={"missing": arg})
        self.assertIn("missing", sig.unresolved)

    def testOrderedFieldIsPersisted(self) -> None:
        """
        Assert that the ordered dict is stored correctly.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument("a")
        sig = _make_signature(ordered={"a": arg})
        self.assertIn("a", sig.ordered)

    def testIsFrozenDataclass(self) -> None:
        """
        Assert that Signature raises FrozenInstanceError on mutation.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = _make_signature()
        with self.assertRaises(FrozenInstanceError):
            sig.ordered = {}  # type: ignore[misc]

    def testNoArgumentsRequiredWhenOrderedIsEmpty(self) -> None:
        """
        Assert that noArgumentsRequired returns True when ordered is empty.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = _make_signature()
        self.assertTrue(sig.noArgumentsRequired())

    def testNoArgumentsRequiredReturnsFalseWhenOrderedHasItems(self) -> None:
        """
        Assert that noArgumentsRequired returns False when ordered has items.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument()
        sig = _make_signature(ordered={"dep": arg})
        self.assertFalse(sig.noArgumentsRequired())

    def testArgumentsReturnsOrderedItems(self) -> None:
        """
        Assert that arguments() returns items from ordered dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument("svc")
        sig = _make_signature(ordered={"svc": arg})
        items = list(sig.arguments())
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][0], "svc")

    def testHasUnresolvedArgumentsReturnsFalseWhenEmpty(self) -> None:
        """
        Assert that hasUnresolvedArguments returns False when unresolved is empty.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = _make_signature()
        self.assertFalse(sig.hasUnresolvedArguments())

    def testHasUnresolvedArgumentsReturnsTrueWhenPresent(self) -> None:
        """
        Assert that hasUnresolvedArguments returns True when unresolved has items.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument("x", resolved=False)
        sig = _make_signature(unresolved={"x": arg})
        self.assertTrue(sig.hasUnresolvedArguments())

    def testToDictReturnsDict(self) -> None:
        """
        Assert that toDict converts ordered arguments to a plain dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument("svc")
        sig = _make_signature(ordered={"svc": arg})
        result = sig.toDict()
        self.assertIsInstance(result, dict)
        self.assertIn("svc", result)

    def testGetAllOrderedReturnsSameAsOrdered(self) -> None:
        """
        Assert that getAllOrdered returns the ordered dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument("svc")
        ordered = {"svc": arg}
        sig = _make_signature(ordered=ordered)
        self.assertEqual(sig.getAllOrdered(), ordered)

    def testItemsReturnsIterableOfTuples(self) -> None:
        """
        Assert that items() returns name-argument pairs from ordered.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        arg = _make_argument("x")
        sig = _make_signature(ordered={"x": arg})
        pairs = list(sig.items())
        self.assertEqual(pairs[0][0], "x")
        self.assertIs(pairs[0][1], arg)

    def testEqualityBetweenIdenticalSignatures(self) -> None:
        """
        Assert that two Signature instances with equal fields compare equal.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig1 = _make_signature()
        sig2 = _make_signature()
        self.assertEqual(sig1, sig2)
