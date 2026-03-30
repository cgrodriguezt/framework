import types
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

    def testNoOpWhenNotDebug(self) -> None:
        """
        Test that the function returns immediately when debug mode is off.

        When isDebug() returns False the function must exit without raising
        any exception or performing any I/O operations.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        result = before_startup_orionis_generator(app)
        self.assertIsNone(result)

    def testNoOpWhenProduction(self) -> None:
        """
        Test that the function returns immediately when in production mode.

        Even if debug is True, when isProduction() returns True the function
        must exit early without performing any rendering operations.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=True, production=True)
        result = before_startup_orionis_generator(app)
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
        result = before_startup_orionis_generator(app)
        self.assertIsNone(result)

# ===========================================================================
# after_startup_orionis_generator
# ===========================================================================

class TestAfterStartupOrionisGenerator(TestCase):

    def testNoOpWhenNotDebug(self) -> None:
        """
        Test that the function returns immediately when debug mode is off.

        When isDebug() returns False the function must exit without rendering
        the HTTP server status panel or touching the console.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=False)
        result = after_startup_orionis_generator(app)
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
        result = after_startup_orionis_generator(app)
        self.assertIsNone(result)

    def testNoOpWhenDebugFalseAndProductionTrue(self) -> None:
        """
        Test that the function returns immediately when debug is False and
        production is True.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _StubApp(debug=False, production=True)
        result = after_startup_orionis_generator(app)
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
