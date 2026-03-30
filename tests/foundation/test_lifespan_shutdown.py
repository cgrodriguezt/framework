import time
import types
from orionis.test import TestCase
from orionis.foundation.lifespan.shutdown import (
    before_shutdown_orionis_generator,
    after_shutdown_orionis_generator,
    shutdown_orionis_generator,
)

# ---------------------------------------------------------------------------
# Minimal stub that satisfies the IApplication interface for these functions
# ---------------------------------------------------------------------------

class _StubApp:

    def __init__(
        self,
        debug: bool = False,
        production: bool = False,
        start_offset_ns: int = 0,
    ) -> None:
        self._debug = debug
        self._production = production
        # startAt is a nanosecond timestamp used by after_shutdown_orionis_generator
        self.startAt = time.time_ns() - start_offset_ns # NOSONAR

    def isDebug(self) -> bool:
        return self._debug

    def isProduction(self) -> bool:
        return self._production

# ===========================================================================
# before_shutdown_orionis_generator
# ===========================================================================

class TestBeforeShutdownOrionisGenerator(TestCase):

    def testNoOpWhenNotDebug(self) -> None:
        """
        Test that the function returns immediately when debug mode is off.

        When isDebug() returns False the function must exit without performing
        any I/O operations.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        result = before_shutdown_orionis_generator(app)
        self.assertIsNone(result)

    def testNoOpWhenProduction(self) -> None:
        """
        Test that the function returns immediately when in production mode.

        Even if debug is True, when isProduction() returns True the function
        must suppress all rendering.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=True, production=True)
        result = before_shutdown_orionis_generator(app)
        self.assertIsNone(result)

    def testNoOpWhenBothFalse(self) -> None:
        """
        Test that the function returns immediately when both flags are False.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        result = before_shutdown_orionis_generator(app)
        self.assertIsNone(result)

# ===========================================================================
# after_shutdown_orionis_generator
# ===========================================================================

class TestAfterShutdownOrionisGenerator(TestCase):

    def testNoOpWhenNotDebug(self) -> None:
        """
        Test that the function returns immediately when debug mode is off.

        The function must exit before computing uptime or rendering anything.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        result = after_shutdown_orionis_generator(app)
        self.assertIsNone(result)

    def testNoOpWhenProduction(self) -> None:
        """
        Test that the function returns immediately when in production mode.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=True, production=True)
        result = after_shutdown_orionis_generator(app)
        self.assertIsNone(result)

    def testNoOpDoesNotAccessStartAt(self) -> None:
        """
        Test that a no-op execution never raises despite startAt being zero.

        When the print_panel flag is False the function returns early and must
        NOT access app.startAt, so an app without that attribute should work.

        Returns
        -------
        None
            This method does not return a value.
        """

        class _MinimalApp:
            def isDebug(self):
                return False

            def isProduction(self):
                return False

        result = after_shutdown_orionis_generator(_MinimalApp())
        self.assertIsNone(result)

    def testStartAtAttributeIsReadableAsInt(self) -> None:
        """
        Test that a stub app's startAt attribute is usable as an integer
        nanosecond timestamp, matching the contract expected by
        after_shutdown_orionis_generator.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False, start_offset_ns=1_000_000_000)
        self.assertIsInstance(app.startAt, int)
        self.assertGreater(time.time_ns() - app.startAt, 0)

# ===========================================================================
# shutdown_orionis_generator
# ===========================================================================

class TestShutdownOrionisGenerator(TestCase):

    def testReturnsGenerator(self) -> None:
        """
        Test that shutdown_orionis_generator returns a generator object.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        gen = shutdown_orionis_generator(app)
        self.assertIsInstance(gen, types.GeneratorType)

    def testYieldsExactlyOnce(self) -> None:
        """
        Test that the generator yields exactly one value then stops.

        The single yield separates the before-shutdown hook from the
        after-shutdown hook.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        gen = shutdown_orionis_generator(app)
        yielded = next(gen)
        self.assertIsNone(yielded)
        with self.assertRaises(StopIteration):
            next(gen)

    def testGeneratorExhaustionIsClean(self) -> None:
        """
        Test that consuming the generator via a for-loop completes without
        raising any exception, and iterates exactly once.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        iterations = sum(1 for _ in shutdown_orionis_generator(app))
        self.assertEqual(iterations, 1)

    def testGeneratorWithProductionTrue(self) -> None:
        """
        Test full generator execution when production is True (no-op path).

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=True, production=True)
        gen = shutdown_orionis_generator(app)
        next(gen)
        with self.assertRaises(StopIteration):
            next(gen)

    def testGeneratorWithDebugFalse(self) -> None:
        """
        Test full generator execution when debug is False (no-op path).

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        gen = shutdown_orionis_generator(app)
        next(gen)
        with self.assertRaises(StopIteration):
            next(gen)

    def testMultipleIndependentGenerators(self) -> None:
        """
        Test that multiple independent generators from the same app do not
        interfere with each other.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        gen1 = shutdown_orionis_generator(app)
        gen2 = shutdown_orionis_generator(app)
        next(gen1)
        next(gen2)
        with self.assertRaises(StopIteration):
            next(gen1)
        with self.assertRaises(StopIteration):
            next(gen2)
