from __future__ import annotations
import inspect
from abc import ABC
from inspect import isabstract
from orionis.services.log.contracts.log_service import ILogger
from orionis.test import TestCase

class _ConcreteLogger(ILogger):
    """Minimal concrete implementation used to verify the contract."""

    @property
    def name(self) -> str:
        return "concrete_logger"

    def info(self, message: str) -> None: # NOSONAR
        pass

    def error(self, message: str) -> None: # NOSONAR
        pass

    def warning(self, message: str) -> None: # NOSONAR
        pass

    def debug(self, message: str) -> None: # NOSONAR
        pass

    def critical(self, message: str) -> None: # NOSONAR
        pass

    def getLogger(self):
        return None

    def reloadConfiguration(self) -> None: # NOSONAR
        pass

    def switchChannel(self, channel_name: str) -> bool:
        return True

    def close(self) -> None: # NOSONAR
        pass

    def getAvailableChannels(self):
        return []

    def getActiveChannel(self):
        return None

    def getActiveChannels(self):
        return []


class _PartialLogger(ILogger):
    """Subclass implementing only info — intentionally incomplete."""

    @property
    def name(self) -> str:
        return "partial"

    def info(self, message: str) -> None:
        pass

# ===========================================================================
# TestILoggerContract
# ===========================================================================

class TestILoggerContract(TestCase):

    def testInheritsFromABC(self) -> None:
        """
        Assert that ILogger inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(ILogger, ABC))

    def testIsAbstractClass(self) -> None:
        """
        Assert that inspect.isabstract identifies ILogger as abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(isabstract(ILogger))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating ILogger directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ILogger()  # type: ignore[abstract]

    def testNameIsAbstractProperty(self) -> None:
        """
        Assert that 'name' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("name", ILogger.__abstractmethods__)

    def testInfoIsAbstractMethod(self) -> None:
        """
        Assert that 'info' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("info", ILogger.__abstractmethods__)

    def testErrorIsAbstractMethod(self) -> None:
        """
        Assert that 'error' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("error", ILogger.__abstractmethods__)

    def testWarningIsAbstractMethod(self) -> None:
        """
        Assert that 'warning' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("warning", ILogger.__abstractmethods__)

    def testDebugIsAbstractMethod(self) -> None:
        """
        Assert that 'debug' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("debug", ILogger.__abstractmethods__)

    def testCriticalIsAbstractMethod(self) -> None:
        """
        Assert that 'critical' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("critical", ILogger.__abstractmethods__)

    def testAbstractMethodsContainsThirteenMembers(self) -> None:
        """
        Assert that __abstractmethods__ contains exactly thirteen members.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            ILogger.__abstractmethods__,
            frozenset({
                "name", "info", "error", "warning", "debug", "critical",
                "getLogger", "reloadConfiguration", "switchChannel",
                "close", "getAvailableChannels", "getActiveChannel", "getActiveChannels",
            }),
        )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Assert that a subclass missing methods cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _PartialLogger()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Assert that a fully implemented subclass can be created without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteLogger()
        self.assertIsInstance(instance, ILogger)

    def testConcreteNameReturnsString(self) -> None:
        """
        Assert that a concrete name property returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteLogger()
        self.assertIsInstance(instance.name, str)

    def testConcreteInfoDoesNotRaise(self) -> None:
        """
        Assert that a concrete info implementation runs without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteLogger()
        instance.info("test message")

    def testConcreteErrorDoesNotRaise(self) -> None:
        """
        Assert that a concrete error implementation runs without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteLogger()
        instance.error("test error")

    def testConcreteWarningDoesNotRaise(self) -> None:
        """
        Assert that a concrete warning implementation runs without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteLogger()
        instance.warning("test warning")

    def testConcreteDebugDoesNotRaise(self) -> None:
        """
        Assert that a concrete debug implementation runs without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteLogger()
        instance.debug("test debug")

    def testConcreteCriticalDoesNotRaise(self) -> None:
        """
        Assert that a concrete critical implementation runs without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteLogger()
        instance.critical("test critical")

    def testInfoMethodAcceptsMessageParam(self) -> None:
        """
        Assert that info method signature includes a message parameter.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(ILogger.info)
        self.assertIn("message", sig.parameters)
