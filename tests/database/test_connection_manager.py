from __future__ import annotations
from orionis.database.connection_manager import ConnectionManager
from orionis.database.contracts.connection import IConnection
from orionis.database.exceptions import ConnectionNotFoundException
from orionis.test import TestCase

class _StubApp:
    """Minimal application stub exposing the database configuration."""

    def __init__(self, config: dict) -> None:
        self._config = config

    def config(self, key: str) -> dict:  # noqa: ARG002
        return self._config

def _makeManager() -> ConnectionManager:
    """Build a manager with two in-memory sqlite connections."""
    return ConnectionManager(_StubApp({
        "default": "sqlite",
        "connections": {
            "sqlite": {"driver": "sqlite", "database": ":memory:", "prefix": ""},
            "replica": {"driver": "sqlite", "database": ":memory:", "prefix": ""},
        },
    }))

class TestConnectionManager(TestCase):

    def setUp(self) -> None:
        """
        Create a fresh manager before each test.

        Guarantees isolation of the connection cache.
        """
        self._manager = _makeManager()

    async def asyncTearDown(self) -> None:
        """
        Dispose every cached connection after each test.

        Releases pooled resources between tests.
        """
        await self._manager.disconnect()

    # ── Resolution ────────────────────────────────────────────────────────────

    def testConnectionResolvesDefault(self) -> None:
        """
        Resolve the default connection when no name is given.

        Validates default connection resolution.
        """
        connection = self._manager.connection()
        self.assertIsInstance(connection, IConnection)
        self.assertEqual(connection.getName(), "sqlite")

    def testConnectionResolvesNamed(self) -> None:
        """
        Resolve a named connection from the configuration.

        Validates named connection resolution.
        """
        connection = self._manager.connection("replica")
        self.assertEqual(connection.getName(), "replica")

    def testConnectionIsCachedPerName(self) -> None:
        """
        Cache connections so repeated access returns the same object.

        Validates the identity of cached connections.
        """
        first = self._manager.connection()
        second = self._manager.connection("sqlite")
        self.assertIs(first, second)

    def testUnknownConnectionRaises(self) -> None:
        """
        Raise ConnectionNotFoundException for unregistered names.

        Validates the descriptive resolution failure.
        """
        with self.assertRaises(ConnectionNotFoundException):
            self._manager.connection("missing")

    # ── Registration ──────────────────────────────────────────────────────────

    def testAddConnectionRegistersConfiguration(self) -> None:
        """
        Register a new connection configuration at runtime.

        Validates the runtime registration entry point.
        """
        self._manager.addConnection(
            "runtime",
            {"driver": "sqlite", "database": ":memory:"},
        )
        self.assertTrue(self._manager.hasConnection("runtime"))
        self.assertEqual(
            self._manager.connection("runtime").getName(),
            "runtime",
        )

    def testAddConnectionValidatesArguments(self) -> None:
        """
        Reject empty names and non-mapping configurations.

        Validates the registration guards.
        """
        with self.assertRaises(ValueError):
            self._manager.addConnection("", {})
        with self.assertRaises(TypeError):
            self._manager.addConnection("bad", "not-a-dict")

    # ── Default connection ────────────────────────────────────────────────────

    def testDefaultNameAccessors(self) -> None:
        """
        Read and change the default connection name.

        Validates the default-name accessors and their guard.
        """
        self.assertEqual(self._manager.getDefaultName(), "sqlite")
        self._manager.setDefaultName("replica")
        self.assertEqual(self._manager.connection().getName(), "replica")
        with self.assertRaises(ConnectionNotFoundException):
            self._manager.setDefaultName("missing")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def testDisconnectRemovesCachedConnection(self) -> None:
        """
        Dispose a named connection and drop it from the cache.

        Validates that a fresh instance is built afterwards.
        """
        first = self._manager.connection()
        await self._manager.disconnect("sqlite")
        second = self._manager.connection()
        self.assertIsNot(first, second)
