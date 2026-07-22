from __future__ import annotations
import asyncio
import tempfile
from pathlib import Path
from orionis.cache.locks.lock import CacheLock, _FILE_LOCKS
from orionis.cache.stores.file import FileCacheBackend
from orionis.test import TestCase

class TestCacheLock(TestCase):

    def setUp(self) -> None:
        """
        Create a temporary directory and a FileCacheBackend before each test.

        Provides an isolated backend so every test operates without
        side effects from shared state.
        """
        self._tmpdir = tempfile.TemporaryDirectory()
        self._backend = FileCacheBackend(Path(self._tmpdir.name))

    def tearDown(self) -> None:
        """
        Remove the temporary directory and purge per-key asyncio locks.

        Ensures filesystem resources and the global _FILE_LOCKS dict are
        cleaned up after each test to prevent cross-test contamination.
        """
        self._tmpdir.cleanup()
        _FILE_LOCKS.clear()

    # ── basic acquire / release ───────────────────────────────────────────────

    async def testFileLockAcquireAndRelease(self) -> None:
        """
        Acquire and release a file-based lock without error.

        Validates that the happy-path async context manager usage does
        not raise and the lock is released on exit.
        """
        lock = CacheLock(self._backend, "resource_a")
        async with lock:
            pass  # Lock is held here; no assertion needed beyond no-raise.

    async def testFileLockReturnsContextManagerSelf(self) -> None:
        """
        Return self from __aenter__ so the as-clause works correctly.

        Validates that async with lock as l assigns the CacheLock instance
        to the bound variable.
        """
        lock = CacheLock(self._backend, "self_check")
        async with lock as acquired:
            self.assertIs(acquired, lock)

    async def testFileLockIsReleasedAfterContextExit(self) -> None:
        """
        Release the underlying asyncio.Lock after the context exits.

        Validates that the asyncio.Lock stored in _FILE_LOCKS for the key
        is no longer locked once the CacheLock context exits.
        """
        key = "release_check"
        lock = CacheLock(self._backend, key)
        async with lock:
            pass
        internal = _FILE_LOCKS.get(key)
        self.assertIsNotNone(internal)
        self.assertFalse(internal.locked())  # type: ignore[union-attr]

    async def testFileLockWithNoTimeoutAcquires(self) -> None:
        """
        Acquire a lock when timeout is None (no deadline).

        Validates that passing timeout=None uses a plain asyncio.Lock
        acquire without wrapping it in wait_for.
        """
        lock = CacheLock(self._backend, "no_timeout", timeout=None)
        async with lock:
            key = "no_timeout"
            internal = _FILE_LOCKS.get(key)
            self.assertIsNotNone(internal)
            self.assertTrue(internal.locked())  # type: ignore[union-attr]

    async def testFileLockWithTimeoutAcquires(self) -> None:
        """
        Acquire a lock when a positive timeout is specified.

        Validates that passing a timeout wraps the acquire in
        asyncio.wait_for without raising when the lock is free.
        """
        lock = CacheLock(self._backend, "with_timeout", timeout=2.0)
        async with lock:
            pass

    # ── mutual exclusion ─────────────────────────────────────────────────────

    async def testTwoLocksOnSameKeyAreMutuallyExclusive(self) -> None:
        """
        Prevent two coroutines from holding the same key lock simultaneously.

        Validates mutual exclusion by checking that the second acquire
        cannot enter the critical section while the first is still held.
        """
        key = "exclusive"
        lock_a = CacheLock(self._backend, key)
        lock_b = CacheLock(self._backend, key)

        inside = []

        async def coroutine_a() -> None:
            async with lock_a:
                inside.append("a_start")
                await asyncio.sleep(0.05)
                inside.append("a_end")

        async def coroutine_b() -> None:
            await asyncio.sleep(0.01)  # Let A acquire first.
            async with lock_b:
                inside.append("b_start")

        await asyncio.gather(coroutine_a(), coroutine_b())
        # A must complete before B enters.
        self.assertEqual(inside.index("a_end"), inside.index("b_start") - 1)

    async def testTwoLocksOnDifferentKeysAreIndependent(self) -> None:
        """
        Allow two coroutines to hold locks on different keys simultaneously.

        Validates that namespace isolation prevents lock contention
        between unrelated resources.
        """
        lock_x = CacheLock(self._backend, "key_x")
        lock_y = CacheLock(self._backend, "key_y")

        acquired = []

        async def hold_x() -> None:
            async with lock_x:
                acquired.append("x")
                await asyncio.sleep(0.05)

        async def hold_y() -> None:
            async with lock_y:
                acquired.append("y")
                await asyncio.sleep(0.05)

        await asyncio.gather(hold_x(), hold_y())
        # Both should have been acquired (in whichever order).
        self.assertIn("x", acquired)
        self.assertIn("y", acquired)

    # ── timeout expiry ────────────────────────────────────────────────────────

    async def testFileLockTimeoutRaisesWhenLockHeld(self) -> None:
        """
        Raise asyncio.TimeoutError when the lock cannot be acquired in time.

        Validates that a very short timeout expires while another coroutine
        holds the lock, propagating TimeoutError to the waiting caller.
        """
        key = "tight_timeout"
        holder = CacheLock(self._backend, key)
        waiter = CacheLock(self._backend, key, timeout=0.01)

        async def hold() -> None:
            async with holder:
                await asyncio.sleep(0.2)

        holder_task = asyncio.create_task(hold())
        await asyncio.sleep(0.02)  # Let the holder acquire first.

        with self.assertRaises(asyncio.TimeoutError):
            async with waiter:
                pass  # Should not reach here.

        await holder_task
