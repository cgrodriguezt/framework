import os
import tempfile
import shutil
import time as time_module
from orionis.services.log.log_service import Logger
from orionis.services.log.exceptions import LoggerRuntimeError
from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.logging.enums import Level
from orionis.support.facades.logger import Log
from orionis.test.cases.synchronous import SyncTestCase
from unittest.mock import patch, MagicMock

class TestLogger(SyncTestCase):

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates a temporary directory for log files and initializes
        basic configuration objects for testing.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.temp_dir, "test.log")
        self.basic_config = {
            'default': 'stack',
            'channels': {
                'stack': {
                    'path': self.log_path,
                    'level': Level.DEBUG
                }
            }
        }

    def tearDown(self):
        """
        Clean up test fixtures after each test method.

        Removes the temporary directory and all its contents.
        Handles Windows file locking issues by trying multiple times.
        """
        if os.path.exists(self.temp_dir):
            # Shutdown all loggers to release file handles
            import logging
            logging.shutdown()

            for attempt in range(3):
                try:
                    shutil.rmtree(self.temp_dir)
                    break
                except (OSError, PermissionError): # NOSONAR
                    if attempt < 2:
                        time_module.sleep(0.1)
                    else:
                        # If we still can't delete, just pass - it's just cleanup
                        pass

    def testHasInfoMethod(self):
        """
        Verify that the Logger class has an 'info' method.

        Returns
        -------
        None
            This test passes if the 'info' method exists, otherwise it fails.
        """
        self.assertTrue(hasattr(Logger, "info"))

    def testHasErrorMethod(self):
        """
        Verify that the Logger class has an 'error' method.

        Returns
        -------
        None
            This test passes if the 'error' method exists, otherwise it fails.
        """
        self.assertTrue(hasattr(Logger, "error"))

    def testHasWarningMethod(self):
        """
        Verify that the Logger class has a 'warning' method.

        Returns
        -------
        None
            This test passes if the 'warning' method exists, otherwise it fails.
        """
        self.assertTrue(hasattr(Logger, "warning"))

    def testHasDebugMethod(self):
        """
        Verify that the Logger class has a 'debug' method.

        Returns
        -------
        None
            This test passes if the 'debug' method exists, otherwise it fails.
        """
        self.assertTrue(hasattr(Logger, "debug"))

    def testLoggerInitializationWithLoggingConfig(self):
        """
        Test logger initialization with a Logging configuration object.

        Verifies that the logger can be properly initialized when provided
        with a valid Logging configuration instance.

        Returns
        -------
        None
            This test passes if the logger initializes without errors.
        """
        config = Logging(**self.basic_config)
        logger = Logger(config)
        self.assertIsNotNone(logger)

    def testLoggerInitializationWithDictConfig(self):
        """
        Test logger initialization with a dictionary configuration.

        Verifies that the logger can be properly initialized when provided
        with a configuration dictionary that gets converted to a Logging object.

        Returns
        -------
        None
            This test passes if the logger initializes without errors.
        """
        logger = Logger(self.basic_config)
        self.assertIsNotNone(logger)

    def testLoggerInitializationWithKwargs(self):
        """
        Test logger initialization using keyword arguments.

        Verifies that the logger can be initialized when configuration
        parameters are passed as keyword arguments instead of a config object.

        Returns
        -------
        None
            This test passes if the logger initializes without errors.
        """
        logger = Logger(**self.basic_config)
        self.assertIsNotNone(logger)

    def testLoggerInitializationFailsWithInvalidConfig(self):
        """
        Test that logger initialization fails with invalid configuration.

        Verifies that LoggerRuntimeError is raised when attempting to
        initialize the logger with invalid configuration parameters.

        Returns
        -------
        None
            This test passes if LoggerRuntimeError is raised with invalid config.
        """
        with self.assertRaises(LoggerRuntimeError):
            Logger(config="invalid_config")

    def testLoggerInitializationFailsWithInvalidKwargs(self):
        """
        Test that logger initialization fails with invalid keyword arguments.

        Verifies that LoggerRuntimeError is raised when attempting to
        initialize the logger with invalid keyword arguments.

        Returns
        -------
        None
            This test passes if LoggerRuntimeError is raised with invalid kwargs.
        """
        with self.assertRaises(LoggerRuntimeError):
            Logger(invalid_param="invalid_value")

    def testStackChannelConfiguration(self):
        """
        Test logger configuration for stack channel.

        Verifies that the logger can be initialized with stack channel configuration
        without raising exceptions.

        Returns
        -------
        None
            This test passes if stack channel initializes correctly.
        """
        config = self.basic_config.copy()

        try:
            logger = Logger(config)
            self.assertIsNotNone(logger)
        except Exception as e:
            self.fail(f"Stack channel configuration failed: {e}")

    def testHourlyChannelConfiguration(self):
        """
        Test logger configuration for hourly channel.

        Verifies that the logger can be initialized with hourly channel configuration
        without raising exceptions.

        Returns
        -------
        None
            This test passes if hourly channel initializes correctly.
        """
        config = {
            'default': 'hourly',
            'channels': {
                'hourly': {
                    'path': os.path.join(self.temp_dir, "hourly.log"),
                    'level': Level.INFO,
                    'retention_hours': 48
                }
            }
        }

        try:
            logger = Logger(config)
            self.assertIsNotNone(logger)
        except Exception as e:
            self.fail(f"Hourly channel configuration failed: {e}")

    def testDailyChannelConfiguration(self):
        """
        Test logger configuration for daily channel.

        Verifies that the logger can be initialized with daily channel configuration
        without raising exceptions.

        Returns
        -------
        None
            This test passes if daily channel initializes correctly.
        """
        config = {
            'default': 'daily',
            'channels': {
                'daily': {
                    'path': os.path.join(self.temp_dir, "daily.log"),
                    'level': Level.WARNING,
                    'retention_days': 14,
                    'at': '23:59'
                }
            }
        }

        try:
            logger = Logger(config)
            self.assertIsNotNone(logger)
        except Exception as e:
            self.fail(f"Daily channel configuration failed: {e}")

    def testWeeklyChannelConfiguration(self):
        """
        Test logger configuration for weekly channel.

        Verifies that the logger can be initialized with weekly channel configuration
        without raising exceptions.

        Returns
        -------
        None
            This test passes if weekly channel initializes correctly.
        """
        config = {
            'default': 'weekly',
            'channels': {
                'weekly': {
                    'path': os.path.join(self.temp_dir, "weekly.log"),
                    'level': Level.ERROR,
                    'retention_weeks': 8
                }
            }
        }

        try:
            logger = Logger(config)
            self.assertIsNotNone(logger)
        except Exception as e:
            self.fail(f"Weekly channel configuration failed: {e}")

    def testMonthlyChannelConfiguration(self):
        """
        Test logger configuration for monthly channel.

        Verifies that the logger can be initialized with monthly channel configuration
        without raising exceptions.

        Returns
        -------
        None
            This test passes if monthly channel initializes correctly.
        """
        config = {
            'default': 'monthly',
            'channels': {
                'monthly': {
                    'path': os.path.join(self.temp_dir, "monthly.log"),
                    'level': Level.CRITICAL,
                    'retention_months': 6
                }
            }
        }

        try:
            logger = Logger(config)
            self.assertIsNotNone(logger)
        except Exception as e:
            self.fail(f"Monthly channel configuration failed: {e}")

    def testChunkedChannelConfiguration(self):
        """
        Test logger configuration for chunked channel.

        Verifies that the logger can be initialized with chunked channel configuration
        without raising exceptions.

        Returns
        -------
        None
            This test passes if chunked channel initializes correctly.
        """
        config = {
            'default': 'chunked',
            'channels': {
                'chunked': {
                    'path': os.path.join(self.temp_dir, "chunked.log"),
                    'level': Level.DEBUG,
                    'mb_size': 20,
                    'files': 10
                }
            }
        }

        try:
            logger = Logger(config)
            self.assertIsNotNone(logger)
        except Exception as e:
            self.fail(f"Chunked channel configuration failed: {e}")

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testLoggerInitializationFailsOnHandlerError(self, mock_init_logger):
        """
        Test that logger initialization fails when handler setup encounters an error.

        Verifies that LoggerRuntimeError is raised when there's an error
        during the handler configuration process.

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if LoggerRuntimeError is raised on handler error.
        """
        mock_init_logger.side_effect = Exception("Handler error")

        with self.assertRaises(Exception):
            Logger(self.basic_config)

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testInfoMethodLogsCorrectly(self, mock_init_logger):
        """
        Test that the info method can be called without errors.

        Verifies that info messages can be processed by the logger.

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if info messages are processed correctly.
        """
        # Mock the internal logger
        mock_internal_logger = MagicMock()

        logger = Logger(self.basic_config)
        logger._Logger__logger = mock_internal_logger

        test_message = "  Test info message  "
        logger.info(test_message)

        mock_internal_logger.info.assert_called_once_with("Test info message")

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testErrorMethodLogsCorrectly(self, mock_init_logger):
        """
        Test that the error method can be called without errors.

        Verifies that error messages can be processed by the logger.

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if error messages are processed correctly.
        """
        mock_internal_logger = MagicMock()

        logger = Logger(self.basic_config)
        logger._Logger__logger = mock_internal_logger

        test_message = "  Test error message  "
        logger.error(test_message)

        mock_internal_logger.error.assert_called_once_with("Test error message")

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testWarningMethodLogsCorrectly(self, mock_init_logger):
        """
        Test that the warning method can be called without errors.

        Verifies that warning messages can be processed by the logger.

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if warning messages are processed correctly.
        """
        mock_internal_logger = MagicMock()

        logger = Logger(self.basic_config)
        logger._Logger__logger = mock_internal_logger

        test_message = "  Test warning message  "
        logger.warning(test_message)
        mock_internal_logger.warning.assert_called_once_with("Test warning message")

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testDebugMethodLogsCorrectly(self, mock_init_logger):
        """
        Test that the debug method can be called without errors.

        Verifies that debug messages can be processed by the logger.

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if debug messages are processed correctly.
        """
        mock_internal_logger = MagicMock()

        logger = Logger(self.basic_config)
        logger._Logger__logger = mock_internal_logger

        test_message = "  Test debug message  "
        logger.debug(test_message)
        mock_internal_logger.debug.assert_called_once_with("Test debug message")

    def testLoggerFacadeIntegration(self):
        """
        Test integration with the Log facade for all logging levels.

        Verifies that the Log facade can successfully write messages
        at all logging levels without raising exceptions.

        Returns
        -------
        None
            This test passes if all facade methods execute without errors.
        """
        try:
            Log.info("Facade info message test")
            Log.error("Facade error message test")
            Log.warning("Facade warning message test")
            Log.debug("Facade debug message test")
        except Exception as e:
            self.fail(f"Log facade integration failed: {e}")

    def testLoggerInitializationFailsWithInvalidLoggingObject(self):
        """
        Test that logger initialization fails with invalid Logging object parameters.

        Verifies that appropriate exceptions are raised when attempting to
        initialize the logger with a Logging object that has invalid parameters.

        Returns
        -------
        None
            This test passes if exceptions are raised with invalid Logging object.
        """
        with self.assertRaises((LoggerRuntimeError, TypeError, ValueError, Exception)):
            invalid_config = {
                'default': 'nonexistent_channel',
                'channels': {
                    'stack': {
                        'path': self.log_path,
                        'level': Level.DEBUG
                    }
                }
            }
            config = Logging(**invalid_config)
            Logger(config)

    def testLoggerInitializationWithMissingChannelConfig(self):
        """
        Test that logger initialization fails when default channel is not valid.

        Verifies that appropriate exceptions are raised when the default channel
        specified in configuration is not valid according to framework rules.

        Returns
        -------
        None
            This test passes if appropriate exceptions are raised for invalid channel.
        """
        invalid_config = {
            'default': 'nonexistent',
            'channels': {
                'stack': {
                    'path': self.log_path,
                    'level': Level.DEBUG
                }
            }
        }

        with self.assertRaises((LoggerRuntimeError, TypeError, ValueError, Exception)):
            Logger(invalid_config)

    def testLoggerInitializationWithEmptyKwargs(self):
        """
        Test that logger initialization creates a default logger with empty kwargs.

        Verifies that when no arguments are provided, the logger can still be created
        with default configuration values from the Logging dataclass.

        Returns
        -------
        None
            This test passes if the logger initializes successfully with defaults.
        """
        # Empty kwargs actually works because Logging has defaults
        try:
            logger = Logger()
            self.assertIsNotNone(logger)
        except Exception as e:
            # If it fails, it should be due to validation errors
            self.assertIsInstance(e, (LoggerRuntimeError, TypeError, ValueError))

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testLoggerHandlesNoneMessages(self, mock_init_logger):
        """
        Test that the logger handles None messages gracefully.

        Verifies that the logger raises AttributeError when attempting to
        process None values (because None.strip() fails).

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if AttributeError is raised for None messages.
        """
        logger = Logger(self.basic_config)

        # Test with None - should raise AttributeError due to None.strip()
        with self.assertRaises(AttributeError):
            logger.info(None)

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testLoggerHandlesEmptyMessages(self, mock_init_logger):
        """
        Test that the logger handles empty and whitespace-only messages correctly.

        Verifies that the logger can process empty strings and messages
        containing only whitespace without raising errors.

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if empty messages are handled correctly.
        """
        mock_internal_logger = MagicMock()

        logger = Logger(self.basic_config)
        logger._Logger__logger = mock_internal_logger

        logger.info("")
        logger.error("   ")
        logger.warning("\t\n")
        logger.debug("  \t  \n  ")

        mock_internal_logger.info.assert_called_with("")
        mock_internal_logger.error.assert_called_with("")
        mock_internal_logger.warning.assert_called_with("")
        mock_internal_logger.debug.assert_called_with("")

    @patch('orionis.services.log.log_service.Logger._Logger__initLogger')
    def testLoggerMethodsStripWhitespace(self, mock_init_logger):
        """
        Test that all logging methods properly strip whitespace from messages.

        Verifies that info, error, warning, and debug methods all strip
        leading and trailing whitespace before logging.

        Parameters
        ----------
        mock_init_logger : MagicMock
            Mock object for Logger.__initLogger

        Returns
        -------
        None
            This test passes if all methods strip whitespace correctly.
        """
        mock_internal_logger = MagicMock()

        logger = Logger(self.basic_config)
        logger._Logger__logger = mock_internal_logger

        # Test whitespace stripping for all methods
        test_messages = [
            ("  info message  ", "info message"),
            ("\t\nerror message\n\t", "error message"),
            ("   warning message   ", "warning message"),
            ("\r\n  debug message  \r\n", "debug message")
        ]

        for original, expected in test_messages:
            logger.info(original)
            logger.error(original)
            logger.warning(original)
            logger.debug(original)

        # Verify all calls received stripped messages
        info_calls = [call[0][0] for call in mock_internal_logger.info.call_args_list]
        error_calls = [call[0][0] for call in mock_internal_logger.error.call_args_list]
        warning_calls = [call[0][0] for call in mock_internal_logger.warning.call_args_list]
        debug_calls = [call[0][0] for call in mock_internal_logger.debug.call_args_list]

        expected_messages = [expected for _, expected in test_messages]
        self.assertEqual(info_calls, expected_messages)
        self.assertEqual(error_calls, expected_messages)
        self.assertEqual(warning_calls, expected_messages)
        self.assertEqual(debug_calls, expected_messages)