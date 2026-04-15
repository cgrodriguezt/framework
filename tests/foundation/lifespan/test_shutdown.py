import time
import types
from unittest.mock import MagicMock, patch
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
        # startAt is a nanosecond timestamp used by shutdown_orionis_generator
        self.startAt = time.time_ns() - start_offset_ns  # NOSONAR

    def isDebug(self) -> bool:
        return self._debug

    def isProduction(self) -> bool:
        return self._production

# ===========================================================================
# before_shutdown_orionis_generator
# ===========================================================================

class TestBeforeShutdownOrionisGenerator(TestCase):

    def testReturnsNone(self) -> None:
        """
        Test that before_shutdown_orionis_generator always returns None.

        The function takes no arguments and must complete without raising,
        returning None after displaying the shutdown panel.

        Returns
        -------
        None
            This method does not return a value.
        """
        with patch("orionis.foundation.lifespan.shutdown.Console"), \
             patch("orionis.foundation.lifespan.shutdown.time.sleep"):
            result = before_shutdown_orionis_generator() # NOSONAR
        self.assertIsNone(result)

    def testDoesNotRaise(self) -> None:
        """
        Test that before_shutdown_orionis_generator completes without raising
        any exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        with patch("orionis.foundation.lifespan.shutdown.Console"), \
             patch("orionis.foundation.lifespan.shutdown.time.sleep"):
            try:
                before_shutdown_orionis_generator()
            except Exception as exc:
                self.fail(f"before_shutdown_orionis_generator raised unexpectedly: {exc}")

    def testUsesConsoleScreen(self) -> None:
        """
        Test that before_shutdown_orionis_generator enters the
        console.screen() context manager to display the panel.

        Returns
        -------
        None
            This method does not return a value.
        """
        mock_console = MagicMock()
        with patch(
            "orionis.foundation.lifespan.shutdown.Console",
            return_value=mock_console
        ), patch("orionis.foundation.lifespan.shutdown.time.sleep"):
            before_shutdown_orionis_generator()
        mock_console.screen.assert_called_once()

# ===========================================================================
# after_shutdown_orionis_generator
# ===========================================================================

class TestAfterShutdownOrionisGenerator(TestCase):

    def testReturnsNone(self) -> None:
        """
        Test that after_shutdown_orionis_generator returns None for a normal
        nanosecond timestamp.

        Parameters
        ----------
        start_at : int
            A nanosecond timestamp representing a moment 5 seconds in the past.

        Returns
        -------
        None
            This method does not return a value.
        """
        start_at = time.time_ns() - 5_000_000_000
        mock_console = MagicMock()
        mock_console.width = 80
        with patch(
            "orionis.foundation.lifespan.shutdown.Console",
            return_value=mock_console
        ):
            result = after_shutdown_orionis_generator(start_at) # NOSONAR
        self.assertIsNone(result)

    def testElapsedClampedToZeroForFutureTimestamp(self) -> None:
        """
        Test that elapsed time is clamped to zero when start_at is set to a
        future timestamp, preventing negative uptime values.

        Returns
        -------
        None
            This method does not return a value.
        """
        future = time.time_ns() + 10_000_000_000
        mock_console = MagicMock()
        mock_console.width = 80
        with patch(
            "orionis.foundation.lifespan.shutdown.Console",
            return_value=mock_console
        ):
            result = after_shutdown_orionis_generator(future) # NOSONAR
        self.assertIsNone(result)

    def testAcceptsLargeUptime(self) -> None:
        """
        Test that after_shutdown_orionis_generator handles a start_at
        corresponding to a very long uptime (two days) without raising.

        Returns
        -------
        None
            This method does not return a value.
        """
        two_days_ago = time.time_ns() - 172_800_000_000_000
        mock_console = MagicMock()
        mock_console.width = 80
        with patch(
            "orionis.foundation.lifespan.shutdown.Console",
            return_value=mock_console
        ):
            result = after_shutdown_orionis_generator(two_days_ago) # NOSONAR
        self.assertIsNone(result)

    def testStartAtMustBeInt(self) -> None:
        """
        Test that after_shutdown_orionis_generator accepts an integer nanosecond
        timestamp as its sole argument.

        Returns
        -------
        None
            This method does not return a value.
        """
        start_at = time.time_ns() - 1_000_000_000
        self.assertIsInstance(start_at, int)
        mock_console = MagicMock()
        mock_console.width = 80
        with patch(
            "orionis.foundation.lifespan.shutdown.Console",
            return_value=mock_console
        ):
            result = after_shutdown_orionis_generator(start_at) # NOSONAR
        self.assertIsNone(result)

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
