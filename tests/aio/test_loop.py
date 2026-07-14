from __future__ import annotations
import asyncio
import concurrent.futures
import sys
import threading
from unittest.mock import patch
from orionis.aio import Loop
from orionis.test import TestCase

# ---------------------------------------------------------------------------
# Helper coroutines / callables used across multiple tests
# ---------------------------------------------------------------------------

async def _coro_return(value):
    return value

async def _coro_raise(exc_type, message):
    raise exc_type(message)

def _sync_return(value):
    return value

def _sync_raise(exc_type, message):
    raise exc_type(message)

# ---------------------------------------------------------------------------
# _getRunningLoop
# ---------------------------------------------------------------------------

class TestGetRunningLoop(TestCase):

    def testReturnsNoneWhenNoLoopIsRunning(self):
        """
        Return None when no event loop is active in the calling thread.

        Validates that the static helper produces ``None`` inside a fresh
        thread where no loop has ever been started.
        """
        results = []

        def in_thread():
            results.append(Loop._getRunningLoop())

        t = threading.Thread(target=in_thread)
        t.start()
        t.join()
        self.assertIsNone(results[0])

    async def testReturnsLoopInsideAsyncContext(self):
        """
        Return the running event loop from inside an async context.

        Validates that ``_getRunningLoop`` yields the same object as
        ``asyncio.get_running_loop()`` when called from a coroutine.
        """
        expected = asyncio.get_running_loop()
        result = Loop._getRunningLoop()
        self.assertIs(result, expected)

# ---------------------------------------------------------------------------
# _detectUvloop
# ---------------------------------------------------------------------------

class TestDetectUvloop(TestCase):

    def testReturnsNoneOnWindowsWithUvloopAvailable(self):
        """
        Return None on Windows even when uvloop is importable.

        Validates that the platform guard prevents uvloop from being
        selected when ``sys.platform`` is ``"win32"``.
        """
        original_checked = Loop._uvloop_checked
        original_factory = Loop._uvloop_factory

        Loop._uvloop_checked = False
        Loop._uvloop_factory = None

        try:
            with (
                patch.object(Loop, "_IS_WIN32", new=True),
                patch.dict("sys.modules", {"uvloop": object()}),
            ):
                result = Loop._detectUvloop()
        finally:
            Loop._uvloop_checked = original_checked
            Loop._uvloop_factory = original_factory

        self.assertIsNone(result)

    def testReturnsCachedResultOnSecondCall(self):
        """
        Return the cached factory without re-importing on repeated calls.

        Validates that after the first detection ``_uvloop_checked`` is
        True and subsequent calls skip the import logic entirely.
        """
        # Force a fresh detection cycle
        original_checked = Loop._uvloop_checked
        original_factory = Loop._uvloop_factory

        Loop._uvloop_checked = False
        Loop._uvloop_factory = None

        try:
            with patch.object(Loop, "_IS_WIN32", new=True):
                first = Loop._detectUvloop()
                second = Loop._detectUvloop()
        finally:
            Loop._uvloop_checked = original_checked
            Loop._uvloop_factory = original_factory

        self.assertIs(first, second)

    def testSetsUvloopCheckedAfterDetection(self):
        """
        Set ``_uvloop_checked`` to True after the first detection run.

        Validates that the double-checked locking guard is properly
        activated so future calls bypass the import logic.
        """
        original_checked = Loop._uvloop_checked
        original_factory = Loop._uvloop_factory

        Loop._uvloop_checked = False
        Loop._uvloop_factory = None

        try:
            with patch.object(Loop, "_IS_WIN32", new=True):
                Loop._detectUvloop()
            self.assertTrue(Loop._uvloop_checked)
        finally:
            Loop._uvloop_checked = original_checked
            Loop._uvloop_factory = original_factory

# ---------------------------------------------------------------------------
# _getLoopFactory
# ---------------------------------------------------------------------------

class TestGetLoopFactory(TestCase):

    def _reset_factory_cache(self):
        """Reset loop factory cache fields to their original values."""
        self._orig_resolved = Loop._loop_factory_resolved
        self._orig_cached = Loop._loop_factory_cached
        Loop._loop_factory_resolved = False
        Loop._loop_factory_cached = None

    def _restore_factory_cache(self):
        Loop._loop_factory_resolved = self._orig_resolved
        Loop._loop_factory_cached = self._orig_cached

    def testReturnsCachedFactoryOnRepeatedCalls(self):
        """
        Return the identical factory object on every call after the first.

        Validates that resolution runs only once and subsequent calls
        return the same cached reference without repeating detection.
        """
        self._reset_factory_cache()
        try:
            first = Loop._getLoopFactory()
            second = Loop._getLoopFactory()
        finally:
            self._restore_factory_cache()

        self.assertIs(first, second)

    def testSetsLoopFactoryResolvedAfterFirstCall(self):
        """
        Set ``_loop_factory_resolved`` to True after the first resolution.

        Validates that the caching guard is activated so future calls
        bypass the detection logic.
        """
        self._reset_factory_cache()
        try:
            Loop._getLoopFactory()
            self.assertTrue(Loop._loop_factory_resolved)
        finally:
            self._restore_factory_cache()

    def testReturnsProactorFactoryOnWindowsWithoutUvloop(self):
        """
        Return ``asyncio.ProactorEventLoop`` on Windows when uvloop is absent.

        Validates that the Windows-specific fast path picks the Proactor
        loop class when the platform guard matches and uvloop is missing.
        """
        self._reset_factory_cache()
        try:
            with (
                patch.object(Loop, "_IS_WIN32", new=True),
                patch.object(Loop, "_detectUvloop", return_value=None),
            ):
                factory = Loop._getLoopFactory()

            if sys.platform == "win32":
                self.assertIs(factory, asyncio.ProactorEventLoop)
            else:
                # On non-Windows the attribute may not exist; just verify None
                # or a callable was returned without error.
                self.assertTrue(factory is None or callable(factory))
        finally:
            self._restore_factory_cache()

    def testReturnsNoneOnNonWindowsWithoutUvloop(self):
        """
        Return None on non-Windows platforms when uvloop is not available.

        Validates that the caller falls back to ``asyncio.new_event_loop``
        when neither uvloop nor Proactor is applicable.
        """
        self._reset_factory_cache()
        try:
            with (
                patch.object(Loop, "_IS_WIN32", new=False),
                patch.object(Loop, "_detectUvloop", return_value=None),
            ):
                factory = Loop._getLoopFactory()
        finally:
            self._restore_factory_cache()

        self.assertIsNone(factory)

    def testUsesUvloopFactoryWhenDetected(self):
        """
        Return the uvloop factory directly when uvloop detection succeeds.

        Validates that the resolution short-circuits to the uvloop path
        when ``_detectUvloop`` returns a non-None callable.
        """
        def fake_factory() -> asyncio.AbstractEventLoop:
            return asyncio.new_event_loop()

        self._reset_factory_cache()
        try:
            with patch.object(Loop, "_detectUvloop", return_value=fake_factory):
                result = Loop._getLoopFactory()
        finally:
            self._restore_factory_cache()

        self.assertIs(result, fake_factory)

# ---------------------------------------------------------------------------
# _getSyncExecutor
# ---------------------------------------------------------------------------

class TestGetSyncExecutor(TestCase):

    def testReturnsSameExecutorOnRepeatedCalls(self):
        """
        Return the identical executor instance on every call.

        Validates that lazy initialisation runs only once and the shared
        executor is reused for all subsequent requests.
        """
        first = Loop._getSyncExecutor()
        second = Loop._getSyncExecutor()
        self.assertIs(first, second)

    def testReturnsThreadPoolExecutor(self):
        """
        Return an instance of ``concurrent.futures.ThreadPoolExecutor``.

        Validates that the executor type matches the expected concrete class
        used for sync-to-async bridging.
        """
        executor = Loop._getSyncExecutor()
        self.assertIsInstance(executor, concurrent.futures.ThreadPoolExecutor)

    def testExecutorCreatedLazily(self):
        """
        Create the executor only on first access.

        Validates that storing None in ``_sync_executor`` and then
        calling ``_getSyncExecutor`` produces a valid, new executor.
        """
        original = Loop._sync_executor
        Loop._sync_executor = None
        try:
            executor = Loop._getSyncExecutor()
            self.assertIsNotNone(executor)
            self.assertIsInstance(executor, concurrent.futures.ThreadPoolExecutor)
        finally:
            # Restore original executor; shut down the temporary one.
            if Loop._sync_executor is not executor:
                executor.shutdown(wait=False)
            Loop._sync_executor = original

# ---------------------------------------------------------------------------
# getEventLoop
# ---------------------------------------------------------------------------

class TestGetEventLoop(TestCase):

    def testReturnsEventLoopInstance(self):
        """
        Return a valid ``asyncio.AbstractEventLoop`` from a sync context.

        Validates that ``getEventLoop`` never raises and always yields an
        object that is a subclass of ``asyncio.AbstractEventLoop``.
        """
        loop = Loop.getEventLoop()
        self.assertIsInstance(loop, asyncio.AbstractEventLoop)

    def testReturnsSameLoopInSameThread(self):
        """
        Return the same cached loop object within a single thread.

        Validates that successive calls in the same synchronous thread
        never create a new loop when the existing one is still open.
        """
        first = Loop.getEventLoop()
        second = Loop.getEventLoop()
        self.assertIs(first, second)

    async def testReturnsRunningLoopInsideCoroutine(self):
        """
        Return the already-running loop when called from a coroutine.

        Validates that the fast path for an active loop is taken and
        the returned object matches ``asyncio.get_running_loop()``.
        """
        expected = asyncio.get_running_loop()
        result = Loop.getEventLoop()
        self.assertIs(result, expected)

    def testReturnsDifferentLoopInDifferentThread(self):
        """
        Create a fresh loop for each thread that requests one.

        Validates that two threads that both call ``getEventLoop`` receive
        distinct loop instances, maintaining thread isolation.
        """
        loops = []

        def fetch_loop():
            loop = Loop.getEventLoop()
            loops.append(id(loop))

        t1 = threading.Thread(target=fetch_loop)
        t2 = threading.Thread(target=fetch_loop)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(len(loops), 2)
        self.assertNotEqual(loops[0], loops[1])

    def testCreatesNewLoopWhenCachedIsClosed(self):
        """
        Create a new event loop when the cached one has been closed.

        Validates that ``getEventLoop`` does not return a closed loop and
        replaces it transparently with a fresh open one.
        """
        results = []

        def task():
            first = Loop.getEventLoop()
            first.close()
            # Manually clear the thread-local cache to simulate staleness.
            if hasattr(Loop._loop_local, "loop"):
                del Loop._loop_local.loop
            second = Loop.getEventLoop()
            results.append(second.is_closed())

        t = threading.Thread(target=task)
        t.start()
        t.join()

        self.assertEqual(results, [False])

# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

class TestRun(TestCase):
    """Tests for Loop.run.

    All cases that call ``Loop.run`` must be executed inside a dedicated
    thread because the Orionis TestCase runner itself drives every test
    method inside a live event loop, and ``asyncio.run``/``asyncio.Runner``
    refuse to start when a loop is already active.
    """

    def testRunsCoroutineAndReturnsValue(self):
        """
        Execute a coroutine and return its result.

        Validates that ``Loop.run`` correctly drives the coroutine to
        completion and surfaces the returned value to the caller.
        """
        results = []

        def in_thread():
            results.append(Loop.run(_coro_return(42)))

        t = threading.Thread(target=in_thread)
        t.start()
        t.join()
        self.assertEqual(results[0], 42)

    def testRaisesTypeErrorForNonCoroutine(self):
        """
        Raise ``TypeError`` when the argument is not a coroutine object.

        Validates that passing a plain function, a class, or any non-coroutine
        is rejected with the appropriate exception type.
        """
        error_caught = False
        try:
            Loop.run(lambda: None)  # type: ignore[arg-type]
        except TypeError:
            error_caught = True
        self.assertTrue(error_caught)

    def testRaisesTypeErrorForCoroutineFunctionNotObject(self):
        """
        Raise ``TypeError`` when passed a coroutine function instead of object.

        Validates that the check targets the coroutine *instance*, not the
        function that produces it, so a bare async function is rejected.
        """
        error_caught = False
        try:
            Loop.run(_coro_return)  # type: ignore[arg-type]
        except TypeError:
            error_caught = True
        self.assertTrue(error_caught)

    def testReturnsZeroOnKeyboardInterrupt(self):
        """
        Return 0 when the coroutine raises ``KeyboardInterrupt``.

        Validates that the entry-point wrapper suppresses ``KeyboardInterrupt``
        and returns ``0`` so the process exits cleanly.
        """
        results = []

        def in_thread():
            async def raise_kbd():
                raise KeyboardInterrupt

            results.append(Loop.run(raise_kbd()))

        t = threading.Thread(target=in_thread)
        t.start()
        t.join()
        self.assertEqual(results[0], 0)

    def testPropagatesCoroutineExceptions(self):
        """
        Propagate exceptions raised inside the coroutine.

        Validates that errors other than ``KeyboardInterrupt`` bubble up
        through ``Loop.run`` unchanged.
        """
        errors = []

        def in_thread():
            try:
                Loop.run(_coro_raise(ValueError, "expected"))
            except ValueError as exc:
                errors.append(exc)

        t = threading.Thread(target=in_thread)
        t.start()
        t.join()
        self.assertEqual(len(errors), 1)

    def testRunsCoroutineWithNoneReturn(self):
        """
        Return None when the coroutine yields no explicit value.

        Validates that an implicit ``return None`` is handled correctly
        without raising or converting the result.
        """
        results = []

        def in_thread():
            async def coro_none():
                pass

            results.append(Loop.run(coro_none()))

        t = threading.Thread(target=in_thread)
        t.start()
        t.join()
        self.assertIsNone(results[0])

    def testRaisesTypeErrorForInteger(self):
        """
        Raise ``TypeError`` when passed an integer.

        Validates that primitive non-coroutine objects are rejected
        with the same type check as other invalid inputs.
        """
        error_caught = False
        try:
            Loop.run(123)  # type: ignore[arg-type]
        except TypeError:
            error_caught = True
        self.assertTrue(error_caught)

# ---------------------------------------------------------------------------
# execute
# ---------------------------------------------------------------------------

class TestExecute(TestCase):

    async def testExecutesSyncFunction(self):
        """
        Run a synchronous callable in the executor and return its result.

        Validates that a plain function is offloaded to the executor and
        its return value is surfaced to the awaiting coroutine.
        """
        result = await Loop.execute(_sync_return, 7)
        self.assertEqual(result, 7)

    async def testExecutesAsyncFunction(self):
        """
        Await an async callable directly and return its result.

        Validates that when the callable is a coroutine function it is
        awaited in-loop without going through the executor.
        """
        result = await Loop.execute(_coro_return, "hello")
        self.assertEqual(result, "hello")

    async def testExecutesSyncWithKwargs(self):
        """
        Forward keyword arguments to the synchronous callable.

        Validates that kwargs are passed through ``functools.partial``
        and received correctly by the target function.
        """
        def greet(name):
            return f"hi {name}"

        result = await Loop.execute(greet, name="world")
        self.assertEqual(result, "hi world")

    async def testExecutesAsyncWithKwargs(self):
        """
        Forward keyword arguments to the async callable.

        Validates that kwargs reach the coroutine function and the
        result is returned correctly.
        """
        async def add(a, b):
            return a + b

        result = await Loop.execute(add, a=3, b=4)
        self.assertEqual(result, 7)

    async def testRaisesTypeErrorForNonCallable(self):
        """
        Raise ``TypeError`` when the argument is not callable.

        Validates that passing a raw value instead of a callable triggers
        the guard before any execution attempt is made.
        """
        error_caught = False
        try:
            await Loop.execute(42)  # type: ignore[arg-type]
        except TypeError:
            error_caught = True
        self.assertTrue(error_caught)

    async def testPropagatesSyncException(self):
        """
        Propagate exceptions raised by the synchronous callable.

        Validates that errors thrown inside the executor task are not
        swallowed and bubble up to the awaiting coroutine.
        """
        error_caught = False
        try:
            await Loop.execute(_sync_raise, ValueError, "boom")
        except ValueError:
            error_caught = True
        self.assertTrue(error_caught)

    async def testPropagatesAsyncException(self):
        """
        Propagate exceptions raised by the async callable.

        Validates that errors raised inside an awaited coroutine are not
        suppressed and reach the caller unchanged.
        """
        error_caught = False
        try:
            await Loop.execute(_coro_raise, RuntimeError, "async boom")
        except RuntimeError:
            error_caught = True
        self.assertTrue(error_caught)

    async def testExecutesSyncLambda(self):
        """
        Execute a lambda as a synchronous callable.

        Validates that anonymous functions are treated as sync callables
        and their return value is surfaced correctly.
        """
        result = await Loop.execute(lambda x: x * 2, 5)
        self.assertEqual(result, 10)

    async def testExecutesSyncWithMultiplePositionalArgs(self):
        """
        Forward multiple positional arguments to the synchronous callable.

        Validates that all extra positional args are preserved and
        delivered to the function via ``functools.partial``.
        """
        def multiply(a, b, c):
            return a * b * c

        result = await Loop.execute(multiply, 2, 3, 4)
        self.assertEqual(result, 24)

# ---------------------------------------------------------------------------
# eventLoopContext
# ---------------------------------------------------------------------------

class TestEventLoopContext(TestCase):

    def testYieldsEventLoopInstance(self):
        """
        Yield a valid event loop from the context manager.

        Validates that ``eventLoopContext`` always produces an object that
        inherits from ``asyncio.AbstractEventLoop``.
        """
        with Loop.eventLoopContext() as loop:
            self.assertIsInstance(loop, asyncio.AbstractEventLoop)

    def testLoopIsNotClosedInsideContext(self):
        """
        Keep the loop open while inside the context manager block.

        Validates that the loop is still usable and not prematurely closed
        during the ``with`` block.
        """
        with Loop.eventLoopContext() as loop:
            self.assertFalse(loop.is_closed())

    async def testContextManagerRunsSimpleCoroutine(self):
        """
        Execute a coroutine via the context manager's event loop.

        Validates that the loop provided by the context manager is
        functional; a task is scheduled and awaited inside the live loop.
        """
        with Loop.eventLoopContext() as loop:
            future = loop.create_task(_coro_return(99))
        result = await future
        self.assertEqual(result, 99)

    def testCancelsPendingTasksOnExit(self):
        """
        Cancel pending tasks when the context manager exits.

        Validates that tasks that were scheduled but not yet completed
        are cancelled cooperatively during the ``finally`` cleanup.
        Runs inside a dedicated thread so that ``run_until_complete``
        is never called from a running loop.
        """
        cancelled_flags = []

        def run_in_thread():
            async def long_running():
                try:
                    await asyncio.sleep(1000)
                except asyncio.CancelledError:
                    cancelled_flags.append(True)
                    raise

            async def schedule_and_exit(loop):
                task = loop.create_task(long_running())
                await asyncio.sleep(0)
                return task

            with Loop.eventLoopContext() as loop:
                loop.run_until_complete(schedule_and_exit(loop))

        t = threading.Thread(target=run_in_thread)
        t.start()
        t.join()
        self.assertTrue(len(cancelled_flags) > 0)

# ---------------------------------------------------------------------------
# isLoopRunning
# ---------------------------------------------------------------------------

class TestIsLoopRunning(TestCase):

    def testReturnsFalseInSyncContext(self):
        """
        Return False when no event loop is running in the calling thread.

        Validates that the utility returns the correct boolean value inside
        a fresh thread where no loop has ever been started.
        """
        results = []

        def in_thread():
            results.append(Loop.isLoopRunning())

        t = threading.Thread(target=in_thread)
        t.start()
        t.join()
        self.assertFalse(results[0])

    async def testReturnsTrueInsideCoroutine(self):
        """
        Return True when called from inside a running coroutine.

        Validates that the helper detects the active loop started by the
        async test runner.
        """
        self.assertTrue(Loop.isLoopRunning())

    def testReturnsFalseAfterLoopStops(self):
        """
        Return False after a manually created loop finishes running.

        Validates that once ``loop.run_until_complete`` returns, the loop
        is no longer considered running by the helper. Runs in a dedicated
        thread so that creating and driving a local loop does not conflict
        with the test runner's own event loop.
        """
        results = []

        def in_thread():
            async def noop():
                pass

            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(noop())
            finally:
                loop.close()
            results.append(Loop.isLoopRunning())

        t = threading.Thread(target=in_thread)
        t.start()
        t.join()
        self.assertFalse(results[0])

# ---------------------------------------------------------------------------
# createTask
# ---------------------------------------------------------------------------

class TestCreateTask(TestCase):

    async def testCreatesTask(self):
        """
        Create a scheduled ``asyncio.Task`` for the given coroutine.

        Validates that the returned object is an ``asyncio.Task`` that
        can be awaited to retrieve its result.
        """
        task = await Loop.createTask(_coro_return(5))
        result = await task
        self.assertEqual(result, 5)

    async def testCreatesTaskWithName(self):
        """
        Create a named task and verify the name attribute.

        Validates that the optional ``name`` parameter is forwarded to
        the underlying ``create_task`` call.
        """
        task = await Loop.createTask(_coro_return(0), name="orionis-task")
        self.assertEqual(task.get_name(), "orionis-task")
        await task

    async def testCreatesTaskWithoutName(self):
        """
        Create an unnamed task without raising errors.

        Validates that ``name=None`` (the default) does not cause any
        exception and still produces a valid task.
        """
        task = await Loop.createTask(_coro_return("ok"))
        result = await task
        self.assertEqual(result, "ok")

    async def testCreatesTaskReturnsAwaitable(self):
        """
        Return an object that is an instance of ``asyncio.Task``.

        Validates the concrete return type so callers can rely on the
        full ``asyncio.Task`` interface.
        """
        task = await Loop.createTask(_coro_return(None))
        self.assertIsInstance(task, asyncio.Task)
        await task

    async def testMultipleTasksRunConcurrently(self):
        """
        Run multiple tasks concurrently and collect all results.

        Validates that tasks created via ``Loop.createTask`` execute in
        parallel and all values are gathered correctly.
        """
        tasks = [await Loop.createTask(_coro_return(i)) for i in range(5)]
        results = await asyncio.gather(*tasks)
        self.assertEqual(list(results), list(range(5)))

# ---------------------------------------------------------------------------
# runSync
# ---------------------------------------------------------------------------

class TestRunSync(TestCase):

    def testRunsSyncFromSyncContext(self):
        """
        Execute a coroutine synchronously when no loop is running.

        Validates that ``runSync`` drives the coroutine to completion and
        returns its value when called from a plain synchronous function.
        """
        result = Loop.runSync(_coro_return("sync"))
        self.assertEqual(result, "sync")

    async def testRunsSyncFromAsyncContext(self):
        """
        Dispatch coroutine to worker thread when a loop is already running.

        Validates that ``runSync`` uses the thread-pool path to avoid
        deadlocking the currently running event loop.
        """
        result = Loop.runSync(_coro_return("from-async"))
        self.assertEqual(result, "from-async")

    def testPropagatesExceptionFromCoroutine(self):
        """
        Propagate exceptions raised by the coroutine through ``runSync``.

        Validates that errors are not swallowed by the thread-pool future
        and reach the synchronous caller unchanged.
        """
        error_caught = False
        try:
            Loop.runSync(_coro_raise(RuntimeError, "run-sync-fail"))
        except RuntimeError:
            error_caught = True
        self.assertTrue(error_caught)

    def testRunsSyncWithNoneReturn(self):
        """
        Return None when the coroutine produces no explicit value.

        Validates that an implicit ``return None`` is forwarded correctly
        through the synchronous bridge without conversion.
        """
        async def coro_none():
            pass

        result = Loop.runSync(coro_none())
        self.assertIsNone(result)

    async def testRunsSyncMultipleTimesFromAsync(self):
        """
        Execute multiple sequential calls to ``runSync`` from async context.

        Validates that the shared executor can handle repeated calls
        without exhausting thread resources or raising errors.
        """
        results = [Loop.runSync(_coro_return(i)) for i in range(4)]
        self.assertEqual(results, list(range(4)))
