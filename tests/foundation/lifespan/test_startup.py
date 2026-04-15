import types
from unittest.mock import MagicMock, patch
from orionis.test import TestCase
from orionis.foundation.lifespan.startup import (
    before_startup_orionis_generator,
    after_startup_orionis_generator,
    startup_orionis_generator,
)

# ---------------------------------------------------------------------------
# Minimal stub that satisfies the IApplication interface for these functions
# ---------------------------------------------------------------------------

class _StubApp:

    def __init__(
        self,
        debug: bool = False,
        production: bool = False,
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        self._debug = debug
        self._production = production
        self._host = host
        self._port = port

    def isDebug(self) -> bool:
        return self._debug

    def isProduction(self) -> bool:
        return self._production

    def config(self, key: str):
        if key == "app.host":
            return self._host
        if key == "app.port":
            return self._port
        return None

# ===========================================================================
# before_startup_orionis_generator
# ===========================================================================

class TestBeforeStartupOrionisGenerator(TestCase):

    def testReturnsNone(self) -> None:
        """
        Test that before_startup_orionis_generator always returns None.

        The function takes no arguments and must complete without raising,
        returning None after displaying the startup panel.

        Returns
        -------
        None
            This method does not return a value.
        """
        with patch("orionis.foundation.lifespan.startup.Console"), \
             patch("orionis.foundation.lifespan.startup.time.sleep"):
            result = before_startup_orionis_generator() # NOSONAR
        self.assertIsNone(result)

    def testDoesNotRaise(self) -> None:
        """
        Test that before_startup_orionis_generator completes without raising
        any exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        with patch("orionis.foundation.lifespan.startup.Console"), \
             patch("orionis.foundation.lifespan.startup.time.sleep"):
            try:
                before_startup_orionis_generator()
            except Exception as exc:
                self.fail(
                    f"before_startup_orionis_generator raised unexpectedly: {exc}"
                )

    def testUsesConsoleScreen(self) -> None:
        """
        Test that before_startup_orionis_generator enters the
        console.screen() context manager to display the startup panel.

        Returns
        -------
        None
            This method does not return a value.
        """
        mock_console = MagicMock()
        with patch(
            "orionis.foundation.lifespan.startup.Console",
            return_value=mock_console
        ), patch("orionis.foundation.lifespan.startup.time.sleep"):
            before_startup_orionis_generator()
        mock_console.screen.assert_called_once()

# ===========================================================================
# after_startup_orionis_generator
# ===========================================================================

class TestAfterStartupOrionisGenerator(TestCase):

    def _make_mock_loop(self) -> MagicMock:
        """
        Build a MagicMock that stands in for an asyncio event loop.

        Returns
        -------
        MagicMock
            Mock object whose class attributes produce valid name strings.
        """
        return MagicMock()

    def testReturnsNone(self) -> None:
        """
        Test that after_startup_orionis_generator returns None for a standard
        host/port pair.

        Returns
        -------
        None
            This method does not return a value.
        """
        mock_loop = self._make_mock_loop()
        with patch(
            "orionis.foundation.lifespan.startup.Console"
        ), patch(
            "orionis.foundation.lifespan.startup.asyncio.get_running_loop",
            return_value=mock_loop
        ):
            result = after_startup_orionis_generator( # NOSONAR
                host="127.0.0.1", port=8000
            )
        self.assertIsNone(result)

    def testAcceptsCustomHostAndPort(self) -> None:
        """
        Test that after_startup_orionis_generator accepts arbitrary host and
        port values without raising.

        Returns
        -------
        None
            This method does not return a value.
        """
        mock_loop = self._make_mock_loop()
        with patch(
            "orionis.foundation.lifespan.startup.Console"
        ), patch(
            "orionis.foundation.lifespan.startup.asyncio.get_running_loop",
            return_value=mock_loop
        ):
            result = after_startup_orionis_generator( # NOSONAR
                host="192.168.1.1", port=9000
            )
        self.assertIsNone(result)

    def testLoopbackAddressDoesNotRaise(self) -> None:
        """
        Test that passing a loopback address (0.0.0.0) normalizes without
        raising any exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        mock_loop = self._make_mock_loop()
        with patch(
            "orionis.foundation.lifespan.startup.Console"
        ), patch(
            "orionis.foundation.lifespan.startup.asyncio.get_running_loop",
            return_value=mock_loop
        ):
            result = after_startup_orionis_generator( # NOSONAR
                host="0.0.0.0", port=8080
            )
        self.assertIsNone(result)

# ===========================================================================
# startup_orionis_generator
# ===========================================================================

class TestStartupOrionisGenerator(TestCase):

    def testReturnsGenerator(self) -> None:
        """
        Test that startup_orionis_generator returns a generator object.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        gen = startup_orionis_generator(app)
        self.assertIsInstance(gen, types.GeneratorType)

    def testYieldsExactlyOnce(self) -> None:
        """
        Test that the generator yields exactly one value then stops.

        The generator must yield exactly once (after calling
        before_startup_orionis_generator and before calling
        after_startup_orionis_generator).

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        gen = startup_orionis_generator(app)
        yielded = next(gen)
        self.assertIsNone(yielded)
        with self.assertRaises(StopIteration):
            next(gen)

    def testGeneratorExhaustionIsClean(self) -> None:
        """
        Test that consuming the generator via a for-loop completes without
        raising any exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        iterations = sum(1 for _ in startup_orionis_generator(app))
        self.assertEqual(iterations, 1)

    def testGeneratorWithDebugOffAndProductionOff(self) -> None:
        """
        Test full generator execution when both debug and production are False.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        gen = startup_orionis_generator(app)
        # Advance past before-hook
        next(gen)
        # Exhaust generator (triggers after-hook)
        try:
            next(gen)
        except StopIteration:
            pass

    def testGeneratorWithProductionTrue(self) -> None:
        """
        Test full generator execution when production is True (no-op path).

        Even with debug=True, production=True must suppress all UI output.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=True, production=True)
        gen = startup_orionis_generator(app)
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
        gen1 = startup_orionis_generator(app)
        gen2 = startup_orionis_generator(app)
        next(gen1)
        next(gen2)
        with self.assertRaises(StopIteration):
            next(gen1)
        with self.assertRaises(StopIteration):
            next(gen2)
