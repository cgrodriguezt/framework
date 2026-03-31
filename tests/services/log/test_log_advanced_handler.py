from __future__ import annotations
import gzip
import logging
import tempfile
from logging import LogRecord
from pathlib import Path
from orionis.services.log.handlers.advanced_rotating_file_handler import (
    AdvancedRotatingFileHandler,
)
from orionis.services.log.handlers.chunked_suffix_resolver import ChunkedSuffixResolver
from orionis.services.log.handlers.daily_suffix_resolver import DailySuffixResolver
from orionis.services.log.handlers.hourly_suffix_resolver import HourlySuffixResolver
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_handler(
    tmp_dir: str,
    *,
    path_template: str = "logs/app_{suffix}.log",
    resolver: object | None = None,
    max_bytes: int | None = None,
    backup_count: int = 5,
    delay: bool = True,
    compress_rotated: bool = False,
) -> AdvancedRotatingFileHandler:
    """Return a configured AdvancedRotatingFileHandler for tests."""
    if resolver is None:
        resolver = HourlySuffixResolver()
    return AdvancedRotatingFileHandler(
        path_template=path_template,
        suffix_resolver=resolver,
        max_bytes=max_bytes,
        backup_count=backup_count,
        delay=delay,
        compress_rotated=compress_rotated,
        app_root=tmp_dir,
    )

def _make_record(message: str = "test message") -> LogRecord:
    """Return a minimal LogRecord for use in tests."""
    return LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )

# ---------------------------------------------------------------------------
# TestAdvancedRotatingFileHandlerInit
# ---------------------------------------------------------------------------

class TestAdvancedRotatingFileHandlerInit(TestCase):

    def testInitWithDelayDoesNotOpenStream(self) -> None:
        """
        Leave stream as None when delay=True.

        Validates that the handler defers file creation until the first log
        record is emitted when constructed with delay=True.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=True)
            try:
                self.assertIsNone(handler.stream)
            finally:
                handler.close()

    def testInitWithoutDelayOpensStream(self) -> None:
        """
        Open the stream immediately when delay=False.

        Validates that the handler opens the underlying file as soon as it is
        constructed when delay=False.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=False)
            try:
                self.assertIsNotNone(handler.stream)
            finally:
                handler.close()

    def testInitSetsPathTemplate(self) -> None:
        """
        Store the path_template attribute from the constructor argument.

        Validates that the handler correctly records the supplied path_template.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, path_template="logs/custom_{suffix}.log")
            try:
                self.assertEqual(handler.path_template, "logs/custom_{suffix}.log")
            finally:
                handler.close()

    def testInitSetsBackupCount(self) -> None:
        """
        Preserve the backup_count passed to the constructor.

        Validates that backup_count is stored without modification.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, backup_count=10)
            try:
                self.assertEqual(handler.backup_count, 10)
            finally:
                handler.close()

    def testInitSetsMaxBytes(self) -> None:
        """
        Store the max_bytes parameter from the constructor.

        Validates that the max_bytes attribute is correctly initialised
        for chunked (size-based) rotation.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, max_bytes=1024)
            try:
                self.assertEqual(handler.max_bytes, 1024)
            finally:
                handler.close()

# ---------------------------------------------------------------------------
# TestAdvancedRotatingFileHandlerResolvePath
# ---------------------------------------------------------------------------

class TestAdvancedRotatingFileHandlerResolvePath(TestCase):

    def testResolvePathReplacesSuffixPlaceholder(self) -> None:
        """
        Replace the {suffix} placeholder with the provided suffix string.

        Validates that _resolvePath produces a path where {suffix} is
        substituted with the given suffix value.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(
                tmp,
                path_template="logs/app_{suffix}.log",
            )
            try:
                result = handler._resolvePath("2025-04-09_14")
                self.assertIn("2025-04-09_14", result)
                self.assertNotIn("{suffix}", result)
            finally:
                handler.close()

    def testResolvePathCreatesParentDirectory(self) -> None:
        """
        Create any missing parent directories for the resolved log path.

        Validates that _resolvePath calls mkdir(parents=True) so the log
        file can be opened without a FileNotFoundError.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(
                tmp,
                path_template="deep/nested/logs/app_{suffix}.log",
            )
            try:
                handler._resolvePath("test-suffix")
                expected_dir = Path(tmp) / "deep" / "nested" / "logs"
                self.assertTrue(expected_dir.is_dir())
            finally:
                handler.close()

    def testResolvePathReturnsCachedResult(self) -> None:
        """
        Return the cached path on a subsequent call with the same suffix.

        Validates that _resolvePath populates the internal cache so that
        repeated calls with the same suffix return the identical string.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(
                tmp,
                path_template="logs/app_{suffix}.log",
            )
            try:
                first = handler._resolvePath("my-suffix")
                second = handler._resolvePath("my-suffix")
                self.assertEqual(first, second)
            finally:
                handler.close()

    def testResolvePathReturnsDifferentPathForDifferentSuffix(self) -> None:
        """
        Produce distinct paths for different suffixes.

        Validates that two different suffix values yield two different
        resolved paths.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(
                tmp,
                path_template="logs/app_{suffix}.log",
            )
            try:
                path_a = handler._resolvePath("2025-04-09_14")
                path_b = handler._resolvePath("2025-04-09_15")
                self.assertNotEqual(path_a, path_b)
            finally:
                handler.close()

# ---------------------------------------------------------------------------
# TestAdvancedRotatingFileHandlerShouldRotate
# ---------------------------------------------------------------------------

class TestAdvancedRotatingFileHandlerShouldRotate(TestCase):

    def testShouldRotateWhenSuffixChanges(self) -> None:
        """
        Signal rotation when the current suffix differs from the stored one.

        Validates that _shouldRotate returns True after the suffix resolver
        would produce a new suffix compared to handler.current_suffix.
        """
        with tempfile.TemporaryDirectory() as tmp:
            # Use a DailySuffixResolver pinned to a fixed datetime via emit
            handler = _make_handler(
                tmp,
                resolver=DailySuffixResolver(),
            )
            try:
                # Manually set a stale suffix to force a mismatch
                handler.current_suffix = "1970-01-01"
                self.assertTrue(handler._shouldRotate())
            finally:
                handler.close()

    def testShouldRotateWhenFileSizeExceedsMaxBytes(self) -> None:
        """
        Trigger rotation when file_size reaches or exceeds max_bytes.

        Validates that _shouldRotate returns True when the current file
        size is at or above the configured max_bytes threshold.
        """
        with tempfile.TemporaryDirectory() as tmp:
            resolver = HourlySuffixResolver()
            handler = _make_handler(tmp, resolver=resolver, max_bytes=100)
            try:
                # Match suffix to prevent time-based rotation flag
                handler.current_suffix = resolver.getSuffix()
                handler.file_size = 100
                self.assertTrue(handler._shouldRotate())
            finally:
                handler.close()

    def testShouldNotRotateWhenSuffixMatchesAndBelowMaxBytes(self) -> None:
        """
        Return False when the suffix is current and file_size is below max_bytes.

        Validates the steady-state (no rotation needed) path for a handler
        that has both a matching suffix and a small file size.
        """
        with tempfile.TemporaryDirectory() as tmp:
            resolver = HourlySuffixResolver()
            handler = _make_handler(tmp, resolver=resolver, max_bytes=1024 * 1024)
            try:
                handler.current_suffix = resolver.getSuffix()
                handler.file_size = 0
                self.assertFalse(handler._shouldRotate())
            finally:
                handler.close()

    def testShouldNotRotateWhenMaxBytesIsNoneAndSuffixMatches(self) -> None:
        """
        Return False when max_bytes is None and the suffix is unchanged.

        Validates that a time-based handler with a matching suffix does not
        signal rotation.
        """
        with tempfile.TemporaryDirectory() as tmp:
            resolver = HourlySuffixResolver()
            handler = _make_handler(tmp, resolver=resolver, max_bytes=None)
            try:
                handler.current_suffix = resolver.getSuffix()
                self.assertFalse(handler._shouldRotate())
            finally:
                handler.close()

# ---------------------------------------------------------------------------
# TestAdvancedRotatingFileHandlerEmit
# ---------------------------------------------------------------------------

class TestAdvancedRotatingFileHandlerEmit(TestCase):

    def testEmitWritesMessageToFile(self) -> None:
        """
        Write an emitted log record to the underlying log file.

        Validates that the message text appears verbatim in the log file
        after emit() is called.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=True)
            try:
                record = _make_record("hello from test")
                handler.emit(record)
                self.assertIsNotNone(handler.current_path)
                content = Path(handler.current_path).read_text(encoding="utf-8")
                self.assertIn("hello from test", content)
            finally:
                handler.close()

    def testEmitCreatesLogFile(self) -> None:
        """
        Create the log file on disk after the first emit call.

        Validates that no file exists before emit() and that it is created
        after the first emit().
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=True)
            try:
                self.assertIsNone(handler.current_path)
                handler.emit(_make_record("init"))
                self.assertTrue(Path(handler.current_path).exists())
            finally:
                handler.close()

    def testEmitUpdatesFileSize(self) -> None:
        """
        Increment file_size after each emit call.

        Validates that the handler tracks the written byte count by
        verifying that file_size is positive after one emit.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=True)
            try:
                handler.emit(_make_record("size tracking"))
                self.assertGreater(handler.file_size, 0)
            finally:
                handler.close()

    def testEmitAppendsMultipleRecords(self) -> None:
        """
        Append successive log records to the same file.

        Validates that multiple emit() calls do not truncate the file and
        all messages are present in order.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=True)
            try:
                handler.emit(_make_record("first"))
                handler.emit(_make_record("second"))
                content = Path(handler.current_path).read_text(encoding="utf-8")
                self.assertIn("first", content)
                self.assertIn("second", content)
            finally:
                handler.close()

# ---------------------------------------------------------------------------
# TestAdvancedRotatingFileHandlerClose
# ---------------------------------------------------------------------------

class TestAdvancedRotatingFileHandlerClose(TestCase):

    def testCloseReleasesStreamAfterEmit(self) -> None:
        """
        Set stream to None after close() is called.

        Validates that the handler's stream attribute is None once close()
        completes, confirming the file descriptor is released.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=True)
            handler.emit(_make_record("closing test"))
            self.assertIsNotNone(handler.stream)
            handler.close()
            self.assertIsNone(handler.stream)

    def testCloseWithoutEmitDoesNotRaise(self) -> None:
        """
        Close a handler that has never emitted without raising an error.

        Validates that calling close() on an idle handler (stream=None) is
        a no-op and does not raise any exception.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, delay=True)
            # Should not raise
            handler.close()
            self.assertIsNone(handler.stream)

# ---------------------------------------------------------------------------
# TestAdvancedRotatingFileHandlerCompress
# ---------------------------------------------------------------------------

class TestAdvancedRotatingFileHandlerCompress(TestCase):

    def testCompressFileCreatesGzFile(self) -> None:
        """
        Create a gzip-compressed copy of the original log file.

        Validates that _compressFile produces a '.gz' file adjacent to the
        original log file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, compress_rotated=True)
            # Create a dummy log file to compress
            log_path = Path(tmp) / "test.log"
            log_path.write_text("hello compressed world", encoding="utf-8")
            try:
                handler._compressFile(str(log_path))
                gz_path = Path(str(log_path) + ".gz")
                self.assertTrue(gz_path.exists())
            finally:
                handler.close()

    def testCompressFileRemovesOriginal(self) -> None:
        """
        Remove the original log file after successful compression.

        Validates that the source file is deleted once the gzip archive has
        been written successfully.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, compress_rotated=True)
            log_path = Path(tmp) / "test.log"
            log_path.write_text("data to compress", encoding="utf-8")
            try:
                handler._compressFile(str(log_path))
                self.assertFalse(log_path.exists())
            finally:
                handler.close()

    def testCompressFileResultIsValidGzip(self) -> None:
        """
        Produce a valid gzip archive that contains the original content.

        Validates that the compressed file can be opened with gzip and
        its decompressed content matches the original log content.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, compress_rotated=True)
            original_content = b"verifiable gzip content"
            log_path = Path(tmp) / "verify.log"
            log_path.write_bytes(original_content)
            try:
                handler._compressFile(str(log_path))
                gz_path = Path(str(log_path) + ".gz")
                with gzip.open(gz_path, "rb") as f:
                    decompressed = f.read()
                self.assertEqual(decompressed, original_content)
            finally:
                handler.close()

    def testCompressFileHandlesMissingSourceGracefully(self) -> None:
        """
        Handle a non-existent source file without raising an exception.

        Validates that _compressFile silently ignores OSError when the
        target file does not exist.
        """
        with tempfile.TemporaryDirectory() as tmp:
            handler = _make_handler(tmp, compress_rotated=True)
            missing = str(Path(tmp) / "ghost.log")
            try:
                # Must not raise
                handler._compressFile(missing)
            finally:
                handler.close()
