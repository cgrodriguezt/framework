"""
Temporary performance and correctness tests for optimised config entities.

Run with: python -m pytest tests/_perf/test_config_perf.py -v
"""
from __future__ import annotations

import timeit
import unittest

from orionis.foundation.config.startup import Configuration, _SECTION_MAP
from orionis.foundation.config.app.entities.app import App, _ENV_NAMES, _CIPHER_NAMES
from orionis.foundation.config.cache.entities.cache import Cache, _DRIVER_NAMES
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.config.queue.entities.queue import Queue, _BROKER_OPTIONS
from orionis.foundation.config.session.entities.session import (
    Session,
    _SAME_SITE_NAMES,
    _INVALID_COOKIE_CHARS,
)
from orionis.foundation.config.testing.entities.testing import Testing, _VERBOSITY_VALUES
from orionis.foundation.config.database.entities.database import (
    Database,
    _CONNECTION_OPTIONS,
)
from orionis.foundation.config.logging.entities.logging import _CHANNEL_OPTIONS
from orionis.foundation.config.filesystems.entitites.filesystems import (
    Filesystems as _Filesystems,  # noqa: F401
    _DISK_OPTIONS,
)
from orionis.foundation.config.mail.entities.mail import _MAILER_OPTIONS
from orionis.foundation.config.database.entities.sqlite import (
    _FK_NAMES,
    _JOURNAL_NAMES,
    _SYNC_NAMES,
)
from orionis.foundation.config.logging.entities.stack import Stack, _LEVEL_NAMES
from orionis.foundation.config.logging.entities.daily import Daily
from orionis.foundation.config.logging.entities.hourly import Hourly
from orionis.foundation.config.logging.entities.weekly import Weekly
from orionis.foundation.config.logging.entities.monthly import Monthly
from orionis.foundation.config.logging.entities.chunked import Chunked
from orionis.foundation.config.http.entitites.cors import Cors, _ALLOWED_HTTP_METHODS
from orionis.support.entities.base import _FIELDS_CACHE, _dictFactory, _enumSerializer
from enum import Enum


# ---------------------------------------------------------------------------
# Module-level constant correctness
# ---------------------------------------------------------------------------

class TestModuleLevelConstants(unittest.TestCase):
    """Verify all pre-computed frozensets contain the expected values."""

    def testEnvNamesFrozenset(self) -> None:
        """_ENV_NAMES contains all Environments member names."""
        from orionis.foundation.config.app.enums import Environments
        self.assertIsInstance(_ENV_NAMES, frozenset)
        self.assertEqual(_ENV_NAMES, frozenset(Environments._member_names_))

    def testCipherNamesFrozenset(self) -> None:
        """_CIPHER_NAMES contains all Cipher member names."""
        from orionis.foundation.config.app.enums import Cipher
        self.assertIsInstance(_CIPHER_NAMES, frozenset)
        self.assertEqual(_CIPHER_NAMES, frozenset(Cipher._member_names_))

    def testDriverNamesFrozenset(self) -> None:
        """_DRIVER_NAMES contains all Drivers member names."""
        from orionis.foundation.config.cache.enums import Drivers
        self.assertIsInstance(_DRIVER_NAMES, frozenset)
        self.assertEqual(_DRIVER_NAMES, frozenset(Drivers._member_names_))

    def testBrokerOptionsFrozenset(self) -> None:
        """_BROKER_OPTIONS contains broker field names plus 'async'."""
        self.assertIn("database", _BROKER_OPTIONS)
        self.assertIn("async", _BROKER_OPTIONS)

    def testSameSiteNamesFrozenset(self) -> None:
        """_SAME_SITE_NAMES contains all SameSitePolicy member names."""
        from orionis.foundation.config.session.enums import SameSitePolicy
        self.assertIsInstance(_SAME_SITE_NAMES, frozenset)
        self.assertEqual(_SAME_SITE_NAMES, frozenset(SameSitePolicy._member_names_))

    def testInvalidCookieCharsFrozenset(self) -> None:
        """_INVALID_COOKIE_CHARS contains space, semicolon, and comma."""
        self.assertIn(" ", _INVALID_COOKIE_CHARS)
        self.assertIn(";", _INVALID_COOKIE_CHARS)
        self.assertIn(",", _INVALID_COOKIE_CHARS)

    def testVerbosityValuesFrozenset(self) -> None:
        """_VERBOSITY_VALUES covers 0, 1, 2."""
        self.assertEqual(_VERBOSITY_VALUES, {0, 1, 2})

    def testConnectionOptionsFrozenset(self) -> None:
        """_CONNECTION_OPTIONS includes sqlite, mysql, pgsql, oracle."""
        for name in ("sqlite", "mysql", "pgsql", "oracle"):
            self.assertIn(name, _CONNECTION_OPTIONS)

    def testChannelOptionsFrozenset(self) -> None:
        """_CHANNEL_OPTIONS includes standard rotation channels."""
        for name in ("stack", "hourly", "daily", "weekly", "monthly", "chunked"):
            self.assertIn(name, _CHANNEL_OPTIONS)

    def testDiskOptionsFrozenset(self) -> None:
        """_DISK_OPTIONS includes local, public, aws."""
        for name in ("local", "public", "aws"):
            self.assertIn(name, _DISK_OPTIONS)

    def testMailerOptionsFrozenset(self) -> None:
        """_MAILER_OPTIONS includes smtp and file."""
        for name in ("smtp", "file"):
            self.assertIn(name, _MAILER_OPTIONS)

    def testSQLiteFrozensets(self) -> None:
        """SQLite enum name frozensets are non-empty."""
        self.assertTrue(len(_FK_NAMES) > 0)
        self.assertTrue(len(_JOURNAL_NAMES) > 0)
        self.assertTrue(len(_SYNC_NAMES) > 0)

    def testLevelNamesFrozenset(self) -> None:
        """_LEVEL_NAMES covers DEBUG, INFO, WARNING, ERROR, CRITICAL."""
        for name in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            self.assertIn(name, _LEVEL_NAMES)

    def testAllowedHttpMethodsFrozenset(self) -> None:
        """_ALLOWED_HTTP_METHODS includes standard HTTP verbs."""
        for method in ("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"):
            self.assertIn(method, _ALLOWED_HTTP_METHODS)

    def testSectionMapLength(self) -> None:
        """_SECTION_MAP covers all 11 configuration sections."""
        self.assertEqual(len(_SECTION_MAP), 11)
        names = {name for name, _ in _SECTION_MAP}
        for expected in (
            "app", "auth", "cache", "database", "filesystems",
            "http", "logging", "mail", "queue", "session", "testing",
        ):
            self.assertIn(expected, names)


# ---------------------------------------------------------------------------
# BaseEntity optimisations
# ---------------------------------------------------------------------------

class TestBaseEntityOptimisations(unittest.TestCase):
    """Verify module-level dict_factory and per-class field cache."""

    def testEnumSerializerConvertsEnumToValue(self) -> None:
        """_enumSerializer returns the .value of an Enum instance."""

        class _Color(Enum):
            RED = 1

        self.assertEqual(_enumSerializer(_Color.RED), 1)

    def testEnumSerializerPassesThroughNonEnum(self) -> None:
        """_enumSerializer returns non-enum objects unchanged."""
        self.assertEqual(_enumSerializer(42), 42)
        self.assertEqual(_enumSerializer("hello"), "hello")

    def testDictFactoryProducesDict(self) -> None:
        """_dictFactory converts key-value pairs to a dict."""
        result = _dictFactory([("a", 1), ("b", 2)])
        self.assertEqual(result, {"a": 1, "b": 2})

    def testFieldsCachePopulatesOnFirstAccess(self) -> None:
        """_cachedDataclassFields() populates _FIELDS_CACHE for the class."""
        _FIELDS_CACHE.clear()
        _ = App._cachedDataclassFields()
        self.assertIn(App, _FIELDS_CACHE)

    def testFieldsCacheReturnsSameTuple(self) -> None:
        """Second call returns the identical cached tuple object."""
        first = App._cachedDataclassFields()
        second = App._cachedDataclassFields()
        self.assertIs(first, second)

    def testToDictReturnsDict(self) -> None:
        """toDict() produces a plain dict with enum values resolved."""
        cfg = Testing()
        result = cfg.toDict()
        self.assertIsInstance(result, dict)
        self.assertIn("verbosity", result)

    def testGetFieldsReturnsExpectedStructure(self) -> None:
        """getFields() returns a list of dicts with required keys."""
        fields = Testing().getFields()
        self.assertIsInstance(fields, list)
        for entry in fields:
            self.assertIn("name", entry)
            self.assertIn("types", entry)
            self.assertIn("default", entry)
            self.assertIn("metadata", entry)


# ---------------------------------------------------------------------------
# Configuration instantiation and validation
# ---------------------------------------------------------------------------

class TestConfigurationInstantiation(unittest.TestCase):
    """Verify Configuration() constructs successfully with defaults."""

    def testDefaultInstantiation(self) -> None:
        """Configuration() with all defaults should not raise."""
        cfg = Configuration()
        self.assertIsInstance(cfg.app, App)
        self.assertIsInstance(cfg.cache, Cache)
        self.assertIsInstance(cfg.database, Database)

    def testDictSectionCoercedToInstance(self) -> None:
        """Passing a dict for a section converts it to the entity type."""
        cfg = Configuration(testing={"verbosity": 0, "fail_fast": False,
                                     "start_dir": "tests", "file_pattern": "test_*.py",
                                     "method_pattern": "test*", "cache_results": False})
        self.assertIsInstance(cfg.testing, Testing)
        self.assertEqual(cfg.testing.verbosity, 0)

    def testInvalidTypeRaisesTypeError(self) -> None:
        """Passing an invalid type for a section raises TypeError."""
        with self.assertRaises(TypeError):
            Configuration(app=42)  # type: ignore[arg-type]

    def testFrozenImmutability(self) -> None:
        """Configuration is frozen; direct attribute assignment raises FrozenInstanceError."""
        from dataclasses import FrozenInstanceError
        cfg = Configuration()
        with self.assertRaises(FrozenInstanceError):
            cfg.app = App()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# App entity validation
# ---------------------------------------------------------------------------

class TestAppEntity(unittest.TestCase):
    """Verify App() construction and enum normalisation."""

    def testDefaultConstruction(self) -> None:
        """App() with defaults does not raise."""
        app = App()
        self.assertIsInstance(app.name, str)

    def testEnvStringNormalised(self) -> None:
        """A lowercase env string is normalised to its enum value."""
        app = App(env="development")
        self.assertEqual(app.env, "development")

    def testInvalidEnvRaisesValueError(self) -> None:
        """An unrecognised env string raises ValueError."""
        with self.assertRaises(ValueError):
            App(env="INVALID_ENV_999")

    def testCipherStringNormalised(self) -> None:
        """A cipher string with dashes is normalised correctly."""
        app = App(cipher="AES-256-CBC")
        self.assertEqual(app.cipher, "AES-256-CBC")

    def testInvalidCipherRaisesValueError(self) -> None:
        """An unrecognised cipher string raises ValueError."""
        with self.assertRaises(ValueError):
            App(cipher="UNKNOWN-CIPHER")


# ---------------------------------------------------------------------------
# Cache entity validation
# ---------------------------------------------------------------------------

class TestCacheEntity(unittest.TestCase):
    """Verify Cache() driver normalisation."""

    def testDefaultDriverIsFile(self) -> None:
        """Default cache driver is 'file'."""
        cache = Cache()
        self.assertEqual(cache.default, "file")

    def testDriverStringNormalised(self) -> None:
        """A lowercase driver string is normalised to its enum value."""
        cache = Cache(default="file")
        self.assertIsInstance(cache.default, str)

    def testInvalidDriverRaisesValueError(self) -> None:
        """An unrecognised driver raises ValueError."""
        with self.assertRaises(ValueError):
            Cache(default="UNKNOWN_DRIVER")

    def testStoresIsStoresInstance(self) -> None:
        """Stores field is a Stores instance."""
        cache = Cache()
        self.assertIsInstance(cache.stores, Stores)

    def testDictStoresCoerced(self) -> None:
        """A dict for stores is coerced to a Stores instance."""
        cache = Cache(stores={"file": {"driver": "file", "path": "storage/framework/cache/data"}})
        self.assertIsInstance(cache.stores, Stores)


# ---------------------------------------------------------------------------
# Queue entity validation
# ---------------------------------------------------------------------------

class TestQueueEntity(unittest.TestCase):
    """Verify Queue() no longer instantiates Brokers to read field names."""

    def testDefaultInstantiation(self) -> None:
        """Queue() with defaults does not raise."""
        queue = Queue()
        self.assertEqual(queue.default, "async")

    def testInvalidDefaultRaisesValueError(self) -> None:
        """An unrecognised default raises ValueError."""
        with self.assertRaises(ValueError):
            Queue(default="UNKNOWN_QUEUE")

    def testAsyncIsValidDefault(self) -> None:
        """'async' is a valid default even though it is not a Brokers field."""
        queue = Queue(default="async")
        self.assertEqual(queue.default, "async")

    def testDatabaseIsValidDefault(self) -> None:
        """'database' (a Brokers field) is also a valid default."""
        queue = Queue(default="database")
        self.assertEqual(queue.default, "database")


# ---------------------------------------------------------------------------
# Session entity validation
# ---------------------------------------------------------------------------

class TestSessionEntity(unittest.TestCase):
    """Verify Session() validation using pre-cached frozensets."""

    def testDefaultInstantiation(self) -> None:
        """Session() with defaults does not raise; secret_key is str or bytes."""
        session = Session()
        self.assertIsInstance(session.secret_key, (str, bytes))

    def testSameSiteNormalised(self) -> None:
        """A lowercase same_site string is normalised."""
        session = Session(same_site="lax")
        self.assertEqual(session.same_site, "lax")

    def testInvalidSameSiteRaisesValueError(self) -> None:
        """An unrecognised same_site raises ValueError."""
        with self.assertRaises(ValueError):
            Session(same_site="INVALID")

    def testInvalidCookieNameRaisesValueError(self) -> None:
        """A cookie name with a space raises ValueError."""
        with self.assertRaises(ValueError):
            Session(secret_key="x" * 32, session_cookie="bad name")


# ---------------------------------------------------------------------------
# Logging entities validation
# ---------------------------------------------------------------------------

class TestLoggingEntities(unittest.TestCase):
    """Verify logging entity level normalisation without try/except flow."""

    def testStackDefaultLevel(self) -> None:
        """Stack uses INFO level by default."""
        import logging as _logging
        stack = Stack()
        self.assertEqual(stack.level, _logging.INFO)

    def testStackInvalidLevelRaisesValueError(self) -> None:
        """An invalid level string raises ValueError."""
        with self.assertRaises(ValueError):
            Stack(level="NOTEXIST")

    def testDailyDefaultLevel(self) -> None:
        """Daily uses INFO level by default."""
        import logging as _logging
        daily = Daily()
        self.assertEqual(daily.level, _logging.INFO)

    def testDailyInvalidLevelRaisesValueError(self) -> None:
        """An invalid level string raises ValueError in Daily."""
        with self.assertRaises(ValueError):
            Daily(level="BADLEVEL")

    def testMonthlyDefaultLevel(self) -> None:
        """Monthly uses INFO level by default."""
        import logging as _logging
        monthly = Monthly()
        self.assertEqual(monthly.level, _logging.INFO)

    def testMonthlyInvalidLevelRaisesValueError(self) -> None:
        """An invalid level string raises ValueError in Monthly."""
        with self.assertRaises(ValueError):
            Monthly(level="BADLEVEL")

    def testHourlyDefaultRetention(self) -> None:
        """Hourly has retention_hours = 24 by default."""
        hourly = Hourly()
        self.assertEqual(hourly.retention_hours, 24)

    def testWeeklyDefaultLevel(self) -> None:
        """Weekly uses INFO level by default."""
        import logging as _logging
        weekly = Weekly()
        self.assertEqual(weekly.level, _logging.INFO)

    def testChunkedDefaultMbSize(self) -> None:
        """Chunked defaults to mb_size=10."""
        chunked = Chunked()
        self.assertEqual(chunked.mb_size, 10)


# ---------------------------------------------------------------------------
# CORS entity validation
# ---------------------------------------------------------------------------

class TestCorsEntity(unittest.TestCase):
    """Verify Cors validation uses module-level frozenset."""

    def testDefaultInstantiation(self) -> None:
        """Cors() with defaults does not raise."""
        cors = Cors()
        self.assertEqual(cors.allow_origins, ["*"])

    def testValidMethodAccepted(self) -> None:
        """A valid method list is accepted without error."""
        cors = Cors(allow_methods=["GET", "POST"])
        self.assertEqual(cors.allow_methods, ["GET", "POST"])

    def testInvalidMethodRaisesValueError(self) -> None:
        """An unrecognised HTTP method raises ValueError."""
        with self.assertRaises(ValueError):
            Cors(allow_methods=["TELEPORT"])

    def testWildcardBypassesMethodValidation(self) -> None:
        """['*'] bypasses individual method validation."""
        cors = Cors(allow_methods=["*"])
        self.assertEqual(cors.allow_methods, ["*"])


# ---------------------------------------------------------------------------
# File cache entity validation order
# ---------------------------------------------------------------------------

class TestFileCacheEntity(unittest.TestCase):
    """Verify File validation order: type before truthiness."""

    def testIntPathRaisesTypeError(self) -> None:
        """Passing an integer path raises TypeError, not ValueError."""
        with self.assertRaises(TypeError):
            File(path=123)  # type: ignore[arg-type]

    def testEmptyPathRaisesValueError(self) -> None:
        """An empty string path raises ValueError after type check passes."""
        with self.assertRaises(ValueError):
            File(path="")

    def testValidPathConstructsInstance(self) -> None:
        """A valid path string constructs the File instance."""
        f = File(path="storage/framework/cache/data")
        self.assertEqual(f.path, "storage/framework/cache/data")


# ---------------------------------------------------------------------------
# Testing entity validation
# ---------------------------------------------------------------------------

class TestTestingEntity(unittest.TestCase):
    """Verify Testing() verbosity uses pre-cached frozenset."""

    def testDefaultVerbosity(self) -> None:
        """Default verbosity is 2 (DETAILED)."""
        testing = Testing()
        self.assertEqual(testing.verbosity, 2)

    def testValidVerbosityInt(self) -> None:
        """Integer 0 is a valid verbosity level."""
        testing = Testing(verbosity=0)
        self.assertEqual(testing.verbosity, 0)

    def testInvalidVerbosityRaisesTypeError(self) -> None:
        """An out-of-range integer verbosity raises TypeError."""
        with self.assertRaises(TypeError):
            Testing(verbosity=99)


# ---------------------------------------------------------------------------
# Performance benchmarks (informational – do not assert timings)
# ---------------------------------------------------------------------------

class TestPerformanceBenchmarks(unittest.TestCase):
    """Lightweight timing smoke-tests; no hard assertions on speed."""

    def testConfigurationInstantiationCompletes(self) -> None:
        """Configuration() can be instantiated 10 times without error."""
        for _ in range(10):
            cfg = Configuration()
            self.assertIsNotNone(cfg)

    def testToDictRepeatable(self) -> None:
        """toDict() on the same instance returns the same structure each time."""
        cfg = Testing()
        first = cfg.toDict()
        second = cfg.toDict()
        self.assertEqual(first, second)

    def testFieldCacheHitIsIdempotent(self) -> None:
        """Repeated _cachedDataclassFields() calls are O(1) after warm-up."""
        _ = Configuration._cachedDataclassFields()
        t = timeit.timeit(Configuration._cachedDataclassFields, number=10_000)
        # Cache hit should complete 10k lookups well under 1 second
        self.assertLess(t, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
