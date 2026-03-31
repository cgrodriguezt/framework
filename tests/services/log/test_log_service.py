from __future__ import annotations
import logging
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from orionis.services.log.log_service import Logger
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(default: str, channels: dict) -> dict:
    """Return a minimal logging configuration dictionary for tests."""
    return {"default": default, "channels": channels}

_STACK_CHANNEL = {
    "stack": {
        "path": "storage/logs/stack.log",
        "level": logging.INFO,
    }
}

_MULTI_CHANNEL = {
    "stack": {
        "path": "storage/logs/stack.log",
        "level": logging.INFO,
    },
    "daily": {
        "path": "storage/logs/daily_{suffix}.log",
        "level": logging.DEBUG,
        "retention_days": 3,
    },
}

def _make_app(tmp: str, channels: dict = _STACK_CHANNEL) -> MagicMock:
    """
    Build a MagicMock that satisfies the IApplication interface for Logger.

    Parameters
    ----------
    tmp : str
        Temporary directory to use as the application root.
    channels : dict
        Channel configuration dictionary.

    Returns
    -------
    MagicMock
        Mocked application instance.
    """
    app = MagicMock()
    app.config.return_value = _make_config("stack", channels)
    app.path.return_value = tmp
    return app

# ---------------------------------------------------------------------------
# TestLoggerName
# ---------------------------------------------------------------------------

class TestLoggerName(TestCase):

    def testNameReturnsOrionis(self) -> None:
        """
        Return '__orionis__' as the logger name.

        Validates that the name property of Logger always returns the
        hardcoded service name used internally to identify the logger.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            try:
                self.assertEqual(logger.name, "__orionis__")
            finally:
                logger.close()

# ---------------------------------------------------------------------------
# TestLoggerMessages
# ---------------------------------------------------------------------------

class TestLoggerMessages(TestCase):

    def setUp(self) -> None:
        """Prepare a temp directory and a Logger instance for each test."""
        self._tmp = tempfile.mkdtemp()
        Logger._formatter_cache.clear()
        self._app = _make_app(self._tmp)
        self._logger = Logger(self._app)

    def tearDown(self) -> None:
        """Release logger resources and remove the temp directory."""
        self._logger.close()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def testInfoWritesToLogFile(self) -> None:
        """
        Write an INFO-level message to the configured log file.

        Validates that calling info() causes the message to appear in the
        underlying log file on disk.
        """
        self._logger.info("info message test")
        log_path = Path(self._tmp) / "storage" / "logs" / "stack.log"
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("info message test", content)

    def testErrorWritesToLogFile(self) -> None:
        """
        Write an ERROR-level message to the configured log file.

        Validates that error() successfully records the message at ERROR level.
        """
        self._logger.error("error message test")
        log_path = Path(self._tmp) / "storage" / "logs" / "stack.log"
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("error message test", content)

    def testWarningWritesToLogFile(self) -> None:
        """
        Write a WARNING-level message to the configured log file.

        Validates that warning() records the message in the log file.
        """
        self._logger.warning("warning message test")
        log_path = Path(self._tmp) / "storage" / "logs" / "stack.log"
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("warning message test", content)

    def testDebugWritesToLogFile(self) -> None:
        """
        Write a DEBUG-level message when the handler level permits it.

        Validates that debug() records the message when the underlying
        logger level is set to DEBUG or lower.
        """
        # Reconfigure with DEBUG-level stack channel
        self._logger.close()
        debug_app = _make_app(
            self._tmp,
            channels={
                "stack": {
                    "path": "storage/logs/stack.log",
                    "level": logging.DEBUG,
                }
            },
        )
        debug_app.config.return_value = _make_config(
            "stack",
            {
                "stack": {
                    "path": "storage/logs/stack.log",
                    "level": logging.DEBUG,
                }
            },
        )
        self._logger = Logger(debug_app)
        self._logger.debug("debug message test")
        log_path = Path(self._tmp) / "storage" / "logs" / "stack.log"
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("debug message test", content)

    def testCriticalWritesToLogFile(self) -> None:
        """
        Write a CRITICAL-level message to the configured log file.

        Validates that critical() records the message in the log file.
        """
        self._logger.critical("critical message test")
        log_path = Path(self._tmp) / "storage" / "logs" / "stack.log"
        content = log_path.read_text(encoding="utf-8")
        self.assertIn("critical message test", content)

    def testEmptyMessageIsIgnored(self) -> None:
        """
        Silently discard an empty string message without raising.

        Validates that info("") does not write an entry to the log file and
        does not raise any exception.
        """
        self._logger.info("")
        log_path = Path(self._tmp) / "storage" / "logs" / "stack.log"
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8")
            # Either the file is empty or contains no blank lines as entries
            self.assertEqual(content.strip(), "")

    def testWhitespaceOnlyMessageIsIgnored(self) -> None:
        """
        Silently discard a whitespace-only message without raising.

        Validates that info("   ") is stripped and treated as an empty
        message, leaving the log file absent or empty.
        """
        self._logger.info("   ")
        log_path = Path(self._tmp) / "storage" / "logs" / "stack.log"
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8")
            self.assertEqual(content.strip(), "")

# ---------------------------------------------------------------------------
# TestLoggerGetLogger
# ---------------------------------------------------------------------------

class TestLoggerGetLogger(TestCase):

    def testGetLoggerReturnsLoggingLoggerInstance(self) -> None:
        """
        Return a stdlib logging.Logger from getLogger().

        Validates that the internal logger is a standard logging.Logger
        object after initialisation.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            try:
                result = logger.getLogger()
                self.assertIsInstance(result, logging.Logger)
            finally:
                logger.close()

    def testGetLoggerNameMatchesServiceName(self) -> None:
        """
        Return a logger whose name equals the service's name property.

        Validates that the internal logging.Logger was registered under the
        '__orionis__' name in Python's logging hierarchy.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            try:
                internal = logger.getLogger()
                self.assertEqual(internal.name, logger.name)
            finally:
                logger.close()

# ---------------------------------------------------------------------------
# TestLoggerChannelSwitching
# ---------------------------------------------------------------------------

class TestLoggerChannelSwitching(TestCase):

    def testSwitchToValidChannelReturnsTrue(self) -> None:
        """
        Return True when switching to a channel that exists in config.

        Validates that switchChannel succeeds for a configured channel name
        and returns True to indicate success.
        """
        with tempfile.TemporaryDirectory() as tmp:
            app = _make_app(tmp, channels=_MULTI_CHANNEL)
            app.config.return_value = _make_config("stack", _MULTI_CHANNEL)
            logger = Logger(app)
            # Trigger initialisation
            logger.info("initialise")
            try:
                result = logger.switchChannel("daily")
                self.assertTrue(result)
            finally:
                logger.close()

    def testSwitchToInvalidChannelReturnsFalse(self) -> None:
        """
        Return False when switching to a channel absent from config.

        Validates that switchChannel fails gracefully for an unknown channel
        name and returns False without raising.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("initialise")
            try:
                result = logger.switchChannel("nonexistent_channel")
                self.assertFalse(result)
            finally:
                logger.close()

    def testGetAvailableChannelsReturnsConfiguredNames(self) -> None:
        """
        Return all channel names present in the logging configuration.

        Validates that getAvailableChannels lists every key from the
        'channels' section of the config, regardless of whether a handler
        has been activated.
        """
        with tempfile.TemporaryDirectory() as tmp:
            app = _make_app(tmp, channels=_MULTI_CHANNEL)
            app.config.return_value = _make_config("stack", _MULTI_CHANNEL)
            logger = Logger(app)
            try:
                available = logger.getAvailableChannels()
                self.assertIn("stack", available)
                self.assertIn("daily", available)
            finally:
                logger.close()

    def testGetActiveChannelsAfterInit(self) -> None:
        """
        Return the active channel name after the logger is initialised.

        Validates that getActiveChannels() is non-empty once the logger
        has been initialised via a log call.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("trigger init")
            try:
                active = logger.getActiveChannels()
                self.assertGreater(len(active), 0)
            finally:
                logger.close()

    def testGetActiveChannelReturnsFirstActiveChannel(self) -> None:
        """
        Return the name of the first active channel.

        Validates that getActiveChannel() returns a non-None string after
        the logger has been initialised.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("trigger init")
            try:
                channel = logger.getActiveChannel()
                self.assertIsNotNone(channel)
                self.assertIsInstance(channel, str)
            finally:
                logger.close()

    def testGetActiveChannelReturnsNoneBeforeInit(self) -> None:
        """
        Return None when no channel has been activated yet.

        Validates that getActiveChannel() returns None before any log
        method is called (lazy initialisation not yet triggered).
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            try:
                # Do not call any log method – logger not yet initialised
                channel = logger.getActiveChannel()
                self.assertIsNone(channel)
            finally:
                logger.close()

# ---------------------------------------------------------------------------
# TestLoggerReloadConfiguration
# ---------------------------------------------------------------------------

class TestLoggerReloadConfiguration(TestCase):

    def testReloadConfigurationAllowsSubsequentLogging(self) -> None:
        """
        Log messages successfully after reloading the configuration.

        Validates that reloadConfiguration() reinitialises the logger so
        that subsequent log calls write to the file without error.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("before reload")
            logger.reloadConfiguration()
            # Must not raise
            logger.info("after reload")
            try:
                log_path = Path(tmp) / "storage" / "logs" / "stack.log"
                content = log_path.read_text(encoding="utf-8")
                self.assertIn("after reload", content)
            finally:
                logger.close()

    def testReloadConfigurationRaisesOnBrokenAppConfig(self) -> None:
        """
        Raise RuntimeError when the app config call fails during reload.

        Validates that a broken app.config (e.g., raises an exception)
        causes reloadConfiguration to propagate a RuntimeError.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("before broken reload")
            # Make config raise an exception on the next call
            logger._Logger__app.config.side_effect = RuntimeError("config failure")
            try:
                with self.assertRaises(RuntimeError):
                    logger.reloadConfiguration()
            finally:
                # Restore side_effect to allow close() to work
                logger._Logger__app.config.side_effect = None
                logger.close()

# ---------------------------------------------------------------------------
# TestLoggerClose
# ---------------------------------------------------------------------------

class TestLoggerClose(TestCase):

    def testCloseResetsInternalLoggerToNone(self) -> None:
        """
        Set the internal __logger attribute to None after close().

        Validates that close() properly tears down the logger so that the
        next log call would re-initialise it from scratch.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("populate logger")
            logger.close()
            # Access private name-mangled attribute for verification
            self.assertIsNone(logger._Logger__logger)

    def testCloseCanBeCalledMultipleTimes(self) -> None:
        """
        Allow close() to be called repeatedly without raising.

        Validates the idempotency of close() – a second or third call must
        complete silently when the logger is already closed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("populate logger")
            # Multiple close calls must not raise
            logger.close()
            logger.close()

    def testCloseClearsHandlersCache(self) -> None:
        """
        Empty the handlers cache after close() is invoked.

        Validates that getActiveChannels() returns an empty list once the
        logger has been closed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            logger = Logger(_make_app(tmp))
            logger.info("populate logger")
            logger.close()
            self.assertEqual(logger.getActiveChannels(), [])

# ---------------------------------------------------------------------------
# TestLoggerFallbackChannel
# ---------------------------------------------------------------------------

class TestLoggerFallbackChannel(TestCase):

    def testFallbackHandlerUsedWhenDefaultChannelMissing(self) -> None:
        """
        Fall back to a default file handler when the configured channel is absent.

        Validates that the Logger initialises without error and is able to
        write log messages even when the 'default' channel key does not exist
        in the 'channels' dictionary.
        """
        with tempfile.TemporaryDirectory() as tmp:
            # Config references a default channel that is not in channels
            config = _make_config("missing_channel", _STACK_CHANNEL)
            app = MagicMock()
            app.config.return_value = config
            app.path.return_value = tmp
            logger = Logger(app)
            try:
                # Must not raise
                logger.info("fallback channel message")
                active = logger.getActiveChannels()
                self.assertIn("fallback", active)
            finally:
                logger.close()
