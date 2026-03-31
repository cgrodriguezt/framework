from __future__ import annotations
import inspect
from abc import ABC
from datetime import datetime, timezone
from inspect import isabstract
from orionis.services.log.contracts.suffix_resolver import SuffixResolver
from orionis.test import TestCase

class _ConcreteSuffixResolver(SuffixResolver):
    """Minimal concrete implementation used to verify the contract."""

    def getSuffix(self, dt: datetime | None = None) -> str:
        if dt is None:
            dt = datetime.now(tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")

    def getNextRotationTime(self, current_time: datetime) -> datetime:
        from datetime import timedelta
        return current_time + timedelta(days=1)


class _PartialSuffixResolver(SuffixResolver):
    """Subclass implementing only getSuffix — intentionally incomplete."""

    def getSuffix(self, dt: datetime | None = None) -> str:
        return "suffix"

# ===========================================================================
# TestSuffixResolverContract
# ===========================================================================

class TestSuffixResolverContract(TestCase):

    def testInheritsFromABC(self) -> None:
        """
        Assert that SuffixResolver inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(SuffixResolver, ABC))

    def testIsAbstractClass(self) -> None:
        """
        Assert that inspect.isabstract identifies SuffixResolver as abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(isabstract(SuffixResolver))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating SuffixResolver directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            SuffixResolver()  # type: ignore[abstract]

    def testGetSuffixIsAbstractMethod(self) -> None:
        """
        Assert that 'getSuffix' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getSuffix", SuffixResolver.__abstractmethods__)

    def testGetNextRotationTimeIsAbstractMethod(self) -> None:
        """
        Assert that 'getNextRotationTime' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getNextRotationTime", SuffixResolver.__abstractmethods__)

    def testAbstractMethodsContainsTwoMembers(self) -> None:
        """
        Assert that __abstractmethods__ contains exactly getSuffix and getNextRotationTime.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            SuffixResolver.__abstractmethods__,
            frozenset({"getSuffix", "getNextRotationTime"}),
        )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Assert that a subclass missing 'getNextRotationTime' cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _PartialSuffixResolver()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Assert that a fully implemented subclass can be created without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteSuffixResolver()
        self.assertIsInstance(instance, SuffixResolver)

    def testGetSuffixReturnsString(self) -> None:
        """
        Assert that a concrete getSuffix returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteSuffixResolver()
        result = instance.getSuffix()
        self.assertIsInstance(result, str)

    def testGetSuffixAcceptsDatetime(self) -> None:
        """
        Assert that getSuffix accepts an explicit datetime argument.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteSuffixResolver()
        dt = datetime(2026, 3, 31, tzinfo=timezone.utc)
        result = instance.getSuffix(dt)
        self.assertEqual(result, "2026-03-31")

    def testGetNextRotationTimeReturnsDatetime(self) -> None:
        """
        Assert that getNextRotationTime returns a datetime.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteSuffixResolver()
        now = datetime.now(tz=timezone.utc)
        result = instance.getNextRotationTime(now)
        self.assertIsInstance(result, datetime)

    def testGetNextRotationTimeIsAfterCurrentTime(self) -> None:
        """
        Assert that the next rotation time is strictly after current_time.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteSuffixResolver()
        now = datetime.now(tz=timezone.utc)
        result = instance.getNextRotationTime(now)
        self.assertGreater(result, now)

    def testGetSuffixMethodAcceptsOptionalDtParam(self) -> None:
        """
        Assert that getSuffix has a dt parameter with None as default.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(SuffixResolver.getSuffix)
        self.assertIn("dt", sig.parameters)
        self.assertIsNone(sig.parameters["dt"].default)

    def testGetNextRotationTimeAcceptsCurrentTimeParam(self) -> None:
        """
        Assert that getNextRotationTime has a current_time parameter.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(SuffixResolver.getNextRotationTime)
        self.assertIn("current_time", sig.parameters)
