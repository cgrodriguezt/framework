from __future__ import annotations
import tempfile
import time
from pathlib import Path
from orionis.services.cache.file_based_cache import FileBasedCache
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAMPLE_DATA: dict = {"module": "orionis", "version": 1, "active": True}

def _make_cache(
    tmp_dir: str,
    filename: str = "test_cache.json",
    monitored_dirs: list[Path] | None = None,
    monitored_files: list[Path] | None = None,
) -> FileBasedCache:
    """Return a FileBasedCache pointing at *tmp_dir*."""
    return FileBasedCache(
        path=Path(tmp_dir),
        filename=filename,
        monitored_dirs=monitored_dirs,
        monitored_files=monitored_files,
    )

# ---------------------------------------------------------------------------
# TestFileBasedCacheInit
# ---------------------------------------------------------------------------

class TestFileBasedCacheInit(TestCase):

    def testInitCreatesDirectory(self) -> None:
        """
        Create cache directory during initialisation if it does not exist.

        Validates that FileBasedCache automatically creates the given
        path directory on construction.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested = Path(tmp_dir) / "nested" / "deeper"
            FileBasedCache(path=nested, filename="c.json")
            self.assertTrue(nested.exists())

    def testInitRaisesTypeErrorForNonPath(self) -> None:
        """
        Raise TypeError when a non-Path value is passed as path.

        Validates that the constructor enforces the Path type for the
        ``path`` parameter.
        """
        with self.assertRaises(TypeError):
            FileBasedCache(path="/not/a/path/object", filename="c.json")  # type: ignore[arg-type]

    def testInitAcceptsOptionalMonitoredDirs(self) -> None:
        """
        Accept optional monitored_dirs without error.

        Validates that passing a list of directories to monitor does
        not raise any exception during construction.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(
                tmp_dir, monitored_dirs=[Path(tmp_dir)]
            )
            self.assertIsInstance(cache, FileBasedCache)

    def testInitAcceptsOptionalMonitoredFiles(self) -> None:
        """
        Accept optional monitored_files without error.

        Validates that passing a list of files to monitor does not
        raise any exception during construction.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            dummy = Path(tmp_dir) / "dummy.py"
            dummy.write_text("x = 1", encoding="utf-8")
            cache = _make_cache(tmp_dir, monitored_files=[dummy])
            self.assertIsInstance(cache, FileBasedCache)

    def testInitWithNoneMonitoredListsIsValid(self) -> None:
        """
        Accept None for monitored_dirs and monitored_files.

        Validates that the default None values for optional parameters
        do not cause errors during construction.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = FileBasedCache(
                path=Path(tmp_dir),
                filename="c.json",
                monitored_dirs=None,
                monitored_files=None,
            )
            self.assertIsInstance(cache, FileBasedCache)

# ---------------------------------------------------------------------------
# TestFileBasedCacheGet
# ---------------------------------------------------------------------------

class TestFileBasedCacheGet(TestCase):

    def testGetReturnsNoneWhenNoFileExists(self) -> None:
        """
        Return None when no cache file is present on disk.

        Validates that calling get() on a fresh FileBasedCache
        instance returns None before anything has been saved.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            self.assertIsNone(cache.get())

    def testGetReturnsSavedData(self) -> None:
        """
        Return the previously saved data when the cache is valid.

        Validates that data written via save() can be retrieved
        as-is via get().
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save(_SAMPLE_DATA)
            result = cache.get()
            self.assertEqual(result, _SAMPLE_DATA)

    def testGetReturnsNoneAfterClear(self) -> None:
        """
        Return None once the cache file has been cleared.

        Validates that get() returns None after a successful clear()
        call removes the underlying file.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save(_SAMPLE_DATA)
            cache.clear()
            self.assertIsNone(cache.get())

    def testGetReturnsNoneWhenVersionMismatches(self) -> None:
        """
        Return None when the stored cache version does not match.

        Validates that a cache payload with the wrong version number
        is treated as invalid and None is returned.
        """
        import json

        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_file = Path(tmp_dir) / "cache.json"
            # Write a payload with a wrong version directly
            payload = {
                "__meta__": {
                    "version": 999,
                    "generatedAt": int(time.time()),
                    "sourcesHash": "abc",
                },
                "__data__": {"x": 1},
            }
            cache_file.write_text(
                json.dumps(payload), encoding="utf-8"
            )
            cache = _make_cache(tmp_dir)
            self.assertIsNone(cache.get())

    def testGetReturnsNoneWhenMissingMeta(self) -> None:
        """
        Return None when the cache payload lacks a ``__meta__`` key.

        Validates that malformed cache files without metadata are
        treated as invalid.
        """
        import json

        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_file = Path(tmp_dir) / "cache.json"
            payload = {"__data__": {"x": 1}}
            cache_file.write_text(
                json.dumps(payload), encoding="utf-8"
            )
            cache = _make_cache(tmp_dir)
            self.assertIsNone(cache.get())

    def testGetReturnsNoneWhenHashMismatches(self) -> None:
        """
        Return None when the stored sources hash does not match.

        Validates that if a monitored file changes after saving, the
        cached data is invalidated on the next get() call.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            monitored = Path(tmp_dir) / "source.py"
            monitored.write_text("x = 1", encoding="utf-8")

            cache = _make_cache(
                tmp_dir,
                filename="hcache.json",
                monitored_files=[monitored],
            )
            cache.save(_SAMPLE_DATA)

            # Force hash interval to expire then mutate the monitored file
            time.sleep(0.6)
            monitored.write_text("x = 2", encoding="utf-8")

            result = cache.get()
            self.assertIsNone(result)

# ---------------------------------------------------------------------------
# TestFileBasedCacheSave
# ---------------------------------------------------------------------------

class TestFileBasedCacheSave(TestCase):

    def testSaveReturnsTupleWithVersionAndHash(self) -> None:
        """
        Return a tuple of (version, sourcesHash) from save().

        Validates that the save() method returns the cache version
        integer and a non-empty hash string.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            version, sources_hash = cache.save(_SAMPLE_DATA)
            self.assertEqual(version, FileBasedCache.CACHE_VERSION)
            self.assertIsInstance(sources_hash, str)
            self.assertTrue(len(sources_hash) > 0)

    def testSaveRaisesTypeErrorOnNonDict(self) -> None:
        """
        Raise TypeError when save() receives a non-dict argument.

        Validates that passing a list or any non-dict value to save()
        raises TypeError immediately.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            with self.assertRaises(TypeError):
                cache.save(["not", "a", "dict"])  # type: ignore[arg-type]

    def testSaveCreatesFileOnDisk(self) -> None:
        """
        Create the cache file on disk when save() is called.

        Validates that the cache JSON file is physically created after
        a successful save.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save(_SAMPLE_DATA)
            cache_file = Path(tmp_dir) / "test_cache.json"
            self.assertTrue(cache_file.exists())

    def testSaveDoesNotRewriteWhenUnchanged(self) -> None:
        """
        Skip rewriting the cache file when data is unchanged.

        Validates that saving identical data twice does not modify the
        cache file's modification time (optimisation path).
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save(_SAMPLE_DATA)
            cache_file = Path(tmp_dir) / "test_cache.json"
            mtime_after_first = cache_file.stat().st_mtime_ns
            cache.save(_SAMPLE_DATA)
            mtime_after_second = cache_file.stat().st_mtime_ns
            self.assertEqual(mtime_after_first, mtime_after_second)

    def testSaveRewritesWhenDataChanges(self) -> None:
        """
        Rewrite the cache file when the saved data changes.

        Validates that updating the cached data causes the file to be
        overwritten and get() returns the new values.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save({"v": 1})
            cache.save({"v": 2})
            result = cache.get()
            self.assertEqual(result, {"v": 2})

    def testSaveWithEmptyDict(self) -> None:
        """
        Save an empty dictionary without raising an error.

        Validates that an empty dict is a valid input and can be
        recovered via get().
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save({})
            result = cache.get()
            self.assertEqual(result, {})

# ---------------------------------------------------------------------------
# TestFileBasedCacheClear
# ---------------------------------------------------------------------------

class TestFileBasedCacheClear(TestCase):

    def testClearReturnsTrueWhenFileExists(self) -> None:
        """
        Return True from clear() when the cache file exists.

        Validates that clear() successfully removes the cache file
        and reports True.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save(_SAMPLE_DATA)
            result = cache.clear()
            self.assertTrue(result)

    def testClearReturnsFalseWhenNoFile(self) -> None:
        """
        Return False from clear() when no cache file is present.

        Validates that clearing a cache that was never written
        returns False without raising an exception.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            result = cache.clear()
            self.assertFalse(result)

    def testClearRemovesFileFromDisk(self) -> None:
        """
        Remove the cache file from disk when clear() is called.

        Validates that the file is no longer present on the filesystem
        after a successful clear.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save(_SAMPLE_DATA)
            cache_file = Path(tmp_dir) / "test_cache.json"
            self.assertTrue(cache_file.exists())
            cache.clear()
            self.assertFalse(cache_file.exists())

    def testClearCalledTwiceReturnsFalseOnSecond(self) -> None:
        """
        Return False when clear() is called a second time.

        Validates that consecutive clear() calls do not raise an error
        and return False when the file is already gone.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache = _make_cache(tmp_dir)
            cache.save(_SAMPLE_DATA)
            cache.clear()
            result = cache.clear()
            self.assertFalse(result)

# ---------------------------------------------------------------------------
# TestFileBasedCacheMonitoring
# ---------------------------------------------------------------------------

class TestFileBasedCacheMonitoring(TestCase):

    def testMonitoredFileAffectsHash(self) -> None:
        """
        Invalidate the cache when a monitored file changes.

        Validates that modifying a monitored file after saving causes
        get() to return None due to hash mismatch.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "module.py"
            py_file.write_text("value = 1", encoding="utf-8")

            cache = _make_cache(
                tmp_dir,
                filename="mon_cache.json",
                monitored_files=[py_file],
            )
            cache.save({"data": "initial"})

            # Wait for hash cache interval to expire
            time.sleep(0.6)
            # Mutate the monitored file
            py_file.write_text("value = 99", encoding="utf-8")

            self.assertIsNone(cache.get())

    def testMonitoredDirAffectsHash(self) -> None:
        """
        Invalidate the cache when a Python file in a monitored dir changes.

        Validates that modifying any ``.py`` file inside a monitored
        directory causes the cache to be invalidated.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            src_dir = Path(tmp_dir) / "src"
            src_dir.mkdir()
            module_file = src_dir / "mod.py"
            module_file.write_text("x = 0", encoding="utf-8")

            cache = _make_cache(
                tmp_dir,
                filename="dir_cache.json",
                monitored_dirs=[src_dir],
            )
            cache.save({"data": "before"})

            time.sleep(0.6)
            module_file.write_text("x = 100", encoding="utf-8")

            self.assertIsNone(cache.get())

    def testSaveWithMonitoredFilesRoundtrip(self) -> None:
        """
        Persist and retrieve data with monitored files correctly.

        Validates that when monitored files are unchanged between save
        and get, the data is returned intact.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "stable.py"
            py_file.write_text("stable = True", encoding="utf-8")

            cache = _make_cache(
                tmp_dir,
                filename="stable_cache.json",
                monitored_files=[py_file],
            )
            cache.save({"result": "ok"})
            result = cache.get()
            self.assertEqual(result, {"result": "ok"})

    def testNonExistentMonitoredFileIsIgnored(self) -> None:
        """
        Ignore monitored files that do not exist on disk.

        Validates that a non-existent path in monitored_files does not
        raise an error and the cache still operates normally.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            ghost = Path(tmp_dir) / "ghost.py"  # intentionally not created

            cache = _make_cache(
                tmp_dir,
                filename="ghost_cache.json",
                monitored_files=[ghost],
            )
            cache.save(_SAMPLE_DATA)
            result = cache.get()
            self.assertEqual(result, _SAMPLE_DATA)

    def testNonExistentMonitoredDirIsIgnored(self) -> None:
        """
        Ignore monitored directories that do not exist on disk.

        Validates that a missing monitored directory path does not
        cause errors or prevent normal cache operation.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            ghost_dir = Path(tmp_dir) / "nonexistent_dir"

            cache = _make_cache(
                tmp_dir,
                filename="ghostdir_cache.json",
                monitored_dirs=[ghost_dir],
            )
            cache.save(_SAMPLE_DATA)
            result = cache.get()
            self.assertEqual(result, _SAMPLE_DATA)
