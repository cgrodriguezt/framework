from __future__ import annotations
import logging
import tempfile
from pathlib import Path
from orionis.services.log.handlers.advanced_rotating_file_handler import (
    AdvancedRotatingFileHandler,
)
from orionis.services.log.handlers.chunked_suffix_resolver import ChunkedSuffixResolver
from orionis.services.log.handlers.daily_suffix_resolver import DailySuffixResolver
from orionis.services.log.handlers.hourly_suffix_resolver import HourlySuffixResolver
from orionis.services.log.handlers.monthly_suffix_resolver import MonthlySuffixResolver
from orionis.services.log.handlers.rotating_handler_factory import (
    RotatingHandlerFactory,
)
from orionis.services.log.handlers.weekly_suffix_resolver import WeeklySuffixResolver
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# TestRotatingHandlerFactory
# ---------------------------------------------------------------------------

class TestRotatingHandlerFactory(TestCase):

    def testCreateStackHandlerReturnsFileHandler(self) -> None:
        """
        Create a FileHandler for the 'stack' channel.

        Validates that RotatingHandlerFactory returns a standard FileHandler
        instance when the channel name is 'stack'.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {"path": "storage/logs/stack.log", "level": logging.INFO}
            handler = RotatingHandlerFactory.createHandler(
                channel_name="stack",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertIsInstance(handler, logging.FileHandler)
            finally:
                if handler:
                    handler.close()

    def testCreateHourlyHandlerReturnsAdvancedHandler(self) -> None:
        """
        Create an AdvancedRotatingFileHandler for the 'hourly' channel.

        Validates that the factory returns an AdvancedRotatingFileHandler
        with an HourlySuffixResolver attached.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/hourly_{suffix}.log",
                "level": logging.INFO,
                "retention_hours": 24,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="hourly",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertIsInstance(handler, AdvancedRotatingFileHandler)
                self.assertIsInstance(handler.suffix_resolver, HourlySuffixResolver)
            finally:
                if handler:
                    handler.close()

    def testCreateDailyHandlerReturnsAdvancedHandler(self) -> None:
        """
        Create an AdvancedRotatingFileHandler for the 'daily' channel.

        Validates that the factory returns an AdvancedRotatingFileHandler
        with a DailySuffixResolver attached.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/daily_{suffix}.log",
                "level": logging.INFO,
                "retention_days": 7,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="daily",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertIsInstance(handler, AdvancedRotatingFileHandler)
                self.assertIsInstance(handler.suffix_resolver, DailySuffixResolver)
            finally:
                if handler:
                    handler.close()

    def testCreateWeeklyHandlerReturnsAdvancedHandler(self) -> None:
        """
        Create an AdvancedRotatingFileHandler for the 'weekly' channel.

        Validates that the factory returns an AdvancedRotatingFileHandler
        with a WeeklySuffixResolver attached.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/weekly_{suffix}.log",
                "level": logging.INFO,
                "retention_weeks": 4,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="weekly",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertIsInstance(handler, AdvancedRotatingFileHandler)
                self.assertIsInstance(handler.suffix_resolver, WeeklySuffixResolver)
            finally:
                if handler:
                    handler.close()

    def testCreateMonthlyHandlerReturnsAdvancedHandler(self) -> None:
        """
        Create an AdvancedRotatingFileHandler for the 'monthly' channel.

        Validates that the factory returns an AdvancedRotatingFileHandler
        with a MonthlySuffixResolver attached.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/monthly_{suffix}.log",
                "level": logging.INFO,
                "retention_months": 4,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="monthly",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertIsInstance(handler, AdvancedRotatingFileHandler)
                self.assertIsInstance(
                    handler.suffix_resolver, MonthlySuffixResolver
                )
            finally:
                if handler:
                    handler.close()

    def testCreateChunkedHandlerReturnsAdvancedHandler(self) -> None:
        """
        Create an AdvancedRotatingFileHandler for the 'chunked' channel.

        Validates that the factory returns an AdvancedRotatingFileHandler
        with a ChunkedSuffixResolver and the correct max_bytes value.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/chunked_{suffix}.log",
                "level": logging.INFO,
                "mb_size": 10,
                "files": 5,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="chunked",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertIsInstance(handler, AdvancedRotatingFileHandler)
                self.assertIsInstance(handler.suffix_resolver, ChunkedSuffixResolver)
                self.assertEqual(handler.max_bytes, 10 * 1024 * 1024)
            finally:
                if handler:
                    handler.close()

    def testCreateHandlerForUnknownChannelReturnsNone(self) -> None:
        """
        Return None for an unrecognised channel name.

        Validates that the factory gracefully returns None when the channel
        name does not match any supported type.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = RotatingHandlerFactory.createHandler(
                channel_name="unknown_channel",
                channel_config={"path": "storage/logs/x.log", "level": logging.INFO},
                app_root=tmp,
            )
            self.assertIsNone(handler)

    def testStackHandlerRespectsConfiguredLevel(self) -> None:
        """
        Apply the logging level from channel_config to the FileHandler.

        Validates that the created FileHandler level matches the value
        specified in the channel configuration.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {"path": "storage/logs/stack.log", "level": logging.WARNING}
            handler = RotatingHandlerFactory.createHandler(
                channel_name="stack",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertEqual(handler.level, logging.WARNING)
            finally:
                if handler:
                    handler.close()

    def testStackHandlerCreatesParentDirectory(self) -> None:
        """
        Ensure the parent directory of the log file is created.

        Validates that a nested path in the channel config causes the factory
        to create any missing parent directories before returning the handler.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/nested/deep/stack.log",
                "level": logging.INFO,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="stack",
                channel_config=config,
                app_root=tmp,
            )
            try:
                expected_dir = Path(tmp) / "storage" / "logs" / "nested" / "deep"
                self.assertTrue(expected_dir.is_dir())
            finally:
                if handler:
                    handler.close()

    def testChunkedHandlerDefaultMbSizeIsTen(self) -> None:
        """
        Default to 10 MB when mb_size is absent from config.

        Validates that the chunked handler uses 10 MB as max_bytes when no
        explicit mb_size key is present in the config dictionary.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/chunked_{suffix}.log",
                "level": logging.INFO,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="chunked",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertEqual(handler.max_bytes, 10 * 1024 * 1024)
            finally:
                if handler:
                    handler.close()

    def testHourlyHandlerDefaultRetentionIs24(self) -> None:
        """
        Default to 24 as backup_count when retention_hours is absent.

        Validates that the hourly handler uses 24 as backup_count when
        the 'retention_hours' key is missing from the config.
        """
        with tempfile.TemporaryDirectory() as tmp:
            config = {
                "path": "storage/logs/hourly_{suffix}.log",
                "level": logging.INFO,
            }
            handler = RotatingHandlerFactory.createHandler(
                channel_name="hourly",
                channel_config=config,
                app_root=tmp,
            )
            try:
                self.assertEqual(handler.backup_count, 24)
            finally:
                if handler:
                    handler.close()
