import asyncio
import sys
import threading
from orionis.services.asynchrony.engine_cli import ReactorLoop
from orionis.test import TestCase

# ===========================================================================
# TestReactorLoopRun
# ===========================================================================

class TestReactorLoopRun(TestCase):

    @staticmethod
    def _run_in_fresh_thread(coro_factory):
        """
        Helper: execute ``ReactorLoop.run(coro)`` in a thread that has no
        running event loop (as the CLI would).  Returns (result, error).
        """
        result_box: list = []
        error_box: list = []

        def _worker():
            try:
                result_box.append(ReactorLoop.run(coro_factory()))
            except Exception as exc:  # noqa: BLE001
                error_box.append(exc)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join(timeout=10)
        return result_box, error_box

    def testRunReturnsCoroutineResult(self) -> None:
        """
        Test that run() executes the coroutine and returns its value.

        ReactorLoop.run() is a CLI entry-point designed to be called outside
        any running event loop.  The test delegates execution to a fresh
        OS thread so that asyncio.run() can create its own event loop.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return 42

        results, errors = self._run_in_fresh_thread(_coro)
        self.assertFalse(errors, f"Unexpected error: {errors}")
        self.assertEqual(results, [42])

    def testRunWithNonCoroutineIntRaisesTypeError(self) -> None:
        """
        Test that run() raises TypeError when passed a plain integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            ReactorLoop.run(99)  # NOSONAR

    def testRunWithNoneRaisesTypeError(self) -> None:
        """
        Test that run() raises TypeError when passed None.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            ReactorLoop.run(None)  # NOSONAR

    def testRunWithLambdaRaisesTypeError(self) -> None:
        """
        Test that run() raises TypeError when passed a regular lambda (not a coroutine).

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            ReactorLoop.run(lambda: "oops")  # type: ignore[arg-type]

    def testRunWithStringRaisesTypeError(self) -> None:
        """
        Test that run() raises TypeError when passed a plain string.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            ReactorLoop.run("not_a_coroutine")  # type: ignore[arg-type]

    def testRunCoroutineReturningNone(self) -> None:
        """
        Test that run() handles a coroutine that returns None.

        Executed in a fresh thread to avoid conflicts with the test
        framework's running event loop.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            pass

        results, errors = self._run_in_fresh_thread(_coro)
        self.assertFalse(errors, f"Unexpected error: {errors}")
        self.assertEqual(results, [None])

    def testRunCoroutineReturningString(self) -> None:
        """
        Test that run() correctly propagates a string return value.

        Executed in a fresh thread to avoid conflicts with the test
        framework's running event loop.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return "hello"

        results, errors = self._run_in_fresh_thread(_coro)
        self.assertFalse(errors, f"Unexpected error: {errors}")
        self.assertEqual(results, ["hello"])

    def testRunCoroutineWithException(self) -> None:
        """
        Test that run() propagates exceptions raised inside the coroutine.

        Executed in a fresh thread to avoid conflicts with the test
        framework's running event loop.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro():
            raise ValueError("boom")

        _results, errors = self._run_in_fresh_thread(_coro)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ValueError)

# ===========================================================================
# TestReactorLoopIsLoopRunning
# ===========================================================================

class TestReactorLoopIsLoopRunning(TestCase):

    def testIsLoopRunningReturnsFalseInSyncContext(self) -> None:
        """
        Test that isLoopRunning() returns False when no event loop is running.

        The Orionis test framework wraps every test method in an async context,
        so this assertion is verified inside a fresh OS thread that is
        guaranteed to have no running loop.

        Returns
        -------
        None
            This method does not return a value.
        """
        result_box: list[bool] = []

        def _check():
            result_box.append(ReactorLoop.isLoopRunning())

        t = threading.Thread(target=_check, daemon=True)
        t.start()
        t.join(timeout=5)
        self.assertEqual(len(result_box), 1)
        self.assertFalse(result_box[0])

    async def testIsLoopRunningReturnsTrueInsideAsyncContext(self) -> None:
        """
        Test that isLoopRunning() returns True when called from within a running loop.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = ReactorLoop.isLoopRunning()
        self.assertTrue(result)

    def testIsLoopRunningReturnsBool(self) -> None:
        """
        Test that isLoopRunning() always returns a boolean value.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = ReactorLoop.isLoopRunning()
        self.assertIsInstance(result, bool)

# ===========================================================================
# TestReactorLoopGetEventLoop
# ===========================================================================

class TestReactorLoopGetEventLoop(TestCase):

    def testGetEventLoopReturnsAbstractEventLoop(self) -> None:
        """
        Test that getEventLoop() returns an asyncio.AbstractEventLoop instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        loop = ReactorLoop.getEventLoop()
        self.assertIsInstance(loop, asyncio.AbstractEventLoop)

    def testGetEventLoopIsNotClosed(self) -> None:
        """
        Test that the event loop returned by getEventLoop() is not closed.

        Returns
        -------
        None
            This method does not return a value.
        """
        loop = ReactorLoop.getEventLoop()
        self.assertFalse(loop.is_closed())

    async def testGetEventLoopInsideRunningLoopReturnsRunningLoop(self) -> None:
        """
        Test that getEventLoop() returns the currently running loop when called
        from within an async context.

        Returns
        -------
        None
            This method does not return a value.
        """
        running_loop = asyncio.get_running_loop()
        obtained_loop = ReactorLoop.getEventLoop()
        self.assertIs(obtained_loop, running_loop)

    def testGetEventLoopReturnsSameInstanceOnRepeatedCall(self) -> None:
        """
        Test that repeated calls to getEventLoop() in the same thread return
        the same loop object.

        Returns
        -------
        None
            This method does not return a value.
        """
        loop1 = ReactorLoop.getEventLoop()
        loop2 = ReactorLoop.getEventLoop()
        self.assertIs(loop1, loop2)

# ===========================================================================
# TestReactorLoopExecute
# ===========================================================================

class TestReactorLoopExecute(TestCase):

    async def testExecuteSyncCallableReturnsResult(self) -> None:
        """
        Test that execute() calls a sync function and returns its result.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = await ReactorLoop.execute(lambda: 7)
        self.assertEqual(result, 7)

    async def testExecuteAsyncCallableReturnsResult(self) -> None:
        """
        Test that execute() awaits an async function and returns its result.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _async(): # NOSONAR
            return "async_result"

        result = await ReactorLoop.execute(_async)
        self.assertEqual(result, "async_result")

    async def testExecuteWithNonCallableRaisesTypeError(self) -> None:
        """
        Test that execute() raises TypeError when passed a non-callable object.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            await ReactorLoop.execute(42)  # type: ignore[arg-type]

    async def testExecuteWithNoneRaisesTypeError(self) -> None:
        """
        Test that execute() raises TypeError when passed None.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            await ReactorLoop.execute(None)  # type: ignore[arg-type]

    async def testExecutePassesPositionalArgs(self) -> None:
        """
        Test that execute() forwards positional arguments to the callable.

        Returns
        -------
        None
            This method does not return a value.
        """
        def _add(a, b):
            return a + b

        result = await ReactorLoop.execute(_add, 3, 4)
        self.assertEqual(result, 7)

    async def testExecutePassesKeywordArgs(self) -> None:
        """
        Test that execute() forwards keyword arguments to the callable.

        Returns
        -------
        None
            This method does not return a value.
        """
        def _greet(name="world"):
            return f"hello {name}"

        result = await ReactorLoop.execute(_greet, name="orionis")
        self.assertEqual(result, "hello orionis")

    async def testExecuteAsyncPassesArgs(self) -> None:
        """
        Test that execute() forwards arguments to an async callable.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _multiply(x, y): # NOSONAR
            return x * y

        result = await ReactorLoop.execute(_multiply, 6, 7)
        self.assertEqual(result, 42)

    async def testExecuteSyncCallableCalledExactlyOnce(self) -> None:
        """
        Test that execute() invokes a sync callable exactly once.

        This guards against the regression where the sync function was called
        once eagerly and then again inside run_in_executor, causing double
        execution and discarding the first result.

        Returns
        -------
        None
            This method does not return a value.
        """
        call_log: list[int] = []

        def _track():
            call_log.append(1)
            return "tracked"

        result = await ReactorLoop.execute(_track)
        self.assertEqual(result, "tracked")
        self.assertEqual(len(call_log), 1, "Sync callable must be invoked exactly once")

    async def testExecuteSyncWithSideEffectsRunsOnlyOnce(self) -> None:
        """
        Test that a sync function with side effects is executed only once.

        Returns
        -------
        None
            This method does not return a value.
        """
        accumulator: list[str] = []

        def _append():
            accumulator.append("x")

        await ReactorLoop.execute(_append)
        self.assertEqual(accumulator, ["x"])

# ===========================================================================
# TestReactorLoopCreateTask
# ===========================================================================

class TestReactorLoopCreateTask(TestCase):

    async def testCreateTaskReturnsAsyncioTask(self) -> None:
        """
        Test that createTask() returns an asyncio.Task instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return "done"

        task = await ReactorLoop.createTask(_coro())
        self.assertIsInstance(task, asyncio.Task)
        await task

    async def testCreateTaskResultMatchesCoroutineReturn(self) -> None:
        """
        Test that the task's result equals the value returned by the coroutine.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return 99

        task = await ReactorLoop.createTask(_coro())
        result = await task
        self.assertEqual(result, 99)

    async def testCreateTaskWithNameSetsTaskName(self) -> None:
        """
        Test that the optional name parameter is applied to the created task.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return "named"

        task = await ReactorLoop.createTask(_coro(), name="test_task_name")
        self.assertEqual(task.get_name(), "test_task_name")
        await task

    async def testCreateTaskWithoutNameStillReturnsTask(self) -> None:
        """
        Test that createTask() works correctly when no name is provided.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return True

        task = await ReactorLoop.createTask(_coro())
        result = await task
        self.assertTrue(result)

    async def testCreateTaskIsScheduledImmediately(self) -> None:
        """
        Test that the created task begins execution after the next await point.

        Returns
        -------
        None
            This method does not return a value.
        """
        ran: list[bool] = []

        async def _coro(): # NOSONAR
            ran.append(True)

        task = await ReactorLoop.createTask(_coro())
        await asyncio.sleep(0)  # yield control so the task can run
        self.assertTrue(ran)
        await task

# ===========================================================================
# TestReactorLoopEventLoopContext
# ===========================================================================

class TestReactorLoopEventLoopContext(TestCase):

    def testEventLoopContextYieldsAbstractEventLoop(self) -> None:
        """
        Test that eventLoopContext() yields an asyncio.AbstractEventLoop.

        Returns
        -------
        None
            This method does not return a value.
        """
        with ReactorLoop.eventLoopContext() as loop:
            self.assertIsInstance(loop, asyncio.AbstractEventLoop)

    def testEventLoopContextLoopIsNotClosed(self) -> None:
        """
        Test that the event loop yielded by the context manager is not closed.

        Returns
        -------
        None
            This method does not return a value.
        """
        with ReactorLoop.eventLoopContext() as loop:
            self.assertFalse(loop.is_closed())

    def testEventLoopContextCanBeEnteredMultipleTimes(self) -> None:
        """
        Test that eventLoopContext() can be used in successive with-blocks.

        Returns
        -------
        None
            This method does not return a value.
        """
        with ReactorLoop.eventLoopContext() as loop1: # NOSONAR
            pass
        with ReactorLoop.eventLoopContext() as loop2: # NOSONAR
            pass

        self.assertIsInstance(loop1, asyncio.AbstractEventLoop)
        self.assertIsInstance(loop2, asyncio.AbstractEventLoop)

    def testEventLoopContextExitsWithoutError(self) -> None:
        """
        Test that exiting the event loop context does not raise any exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        try:
            with ReactorLoop.eventLoopContext(): # NOSONAR
                pass

        except Exception as exc:  # pragma: no cover
            self.fail(f"eventLoopContext() raised an unexpected exception: {exc}")

# ===========================================================================
# TestReactorLoopRunSync
# ===========================================================================

class TestReactorLoopRunSync(TestCase):

    def testRunSyncReturnsCoroutineResult(self) -> None:
        """
        Test that runSync() executes a coroutine and returns its result.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return "sync_result"

        result = ReactorLoop.runSync(_coro())
        self.assertEqual(result, "sync_result")

    def testRunSyncReturnsNumericResult(self) -> None:
        """
        Test that runSync() correctly returns a numeric result from a coroutine.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            return 2 ** 10

        result = ReactorLoop.runSync(_coro())
        self.assertEqual(result, 1024)

    def testRunSyncReturnsNoneWhenCoroutineReturnsNone(self) -> None:
        """
        Test that runSync() returns None when the coroutine has no explicit return.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro(): # NOSONAR
            pass

        result = ReactorLoop.runSync(_coro())
        self.assertIsNone(result)

    def testRunSyncPropagatesCoroutineException(self) -> None:
        """
        Test that runSync() propagates exceptions raised inside the coroutine.

        Returns
        -------
        None
            This method does not return a value.
        """
        async def _coro():
            raise RuntimeError("sync_error")

        with self.assertRaises(RuntimeError):
            ReactorLoop.runSync(_coro())

# ===========================================================================
# TestReactorLoopDetectUvloop
# ===========================================================================

class TestReactorLoopDetectUvloop(TestCase):
    """Tests for ReactorLoop._detect_uvloop()."""

    def testDetectUvloopReturnsCallableOrNone(self) -> None:
        """
        Test that _detect_uvloop() returns either a callable factory or None.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = ReactorLoop._detect_uvloop()
        if result is not None:
            self.assertTrue(callable(result))

    def testDetectUvloopResultIsCachedAfterFirstCall(self) -> None:
        """
        Test that _detect_uvloop() returns the same cached value on repeated calls.

        Returns
        -------
        None
            This method does not return a value.
        """
        first = ReactorLoop._detect_uvloop()
        second = ReactorLoop._detect_uvloop()
        self.assertIs(first, second)

    def testDetectUvloopSetsCheckedFlag(self) -> None:
        """
        Test that _detect_uvloop() sets the _uvloop_checked flag to True.

        Returns
        -------
        None
            This method does not return a value.
        """
        ReactorLoop._detect_uvloop()
        self.assertTrue(ReactorLoop._uvloop_checked)

    def testDetectUvloopOnWindowsReturnsNone(self) -> None:
        """
        Test that _detect_uvloop() returns None on the Windows platform.

        uvloop is not supported on Windows, so the factory must be None.

        Returns
        -------
        None
            This method does not return a value.
        """
        if sys.platform == "win32":
            result = ReactorLoop._detect_uvloop()
            self.assertIsNone(result)

# ===========================================================================
# TestReactorLoopGetLoopFactory
# ===========================================================================

class TestReactorLoopGetLoopFactory(TestCase):
    """Tests for ReactorLoop._get_loop_factory()."""

    def testGetLoopFactoryReturnsCallableOrNone(self) -> None:
        """
        Test that _get_loop_factory() returns either a callable or None.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = ReactorLoop._get_loop_factory()
        if result is not None:
            self.assertTrue(callable(result))

    def testGetLoopFactoryOnWindowsReturnsNoneOrProactor(self) -> None:
        """
        Test that _get_loop_factory() returns the ProactorEventLoop class or None
        on Windows, depending on availability.

        Returns
        -------
        None
            This method does not return a value.
        """
        if sys.platform == "win32":
            result = ReactorLoop._get_loop_factory()
            # On Windows without uvloop, could be ProactorEventLoop or None
            if result is not None:
                self.assertTrue(callable(result))

    def testGetLoopFactoryReturnValueIsConsistent(self) -> None:
        """
        Test that _get_loop_factory() returns the same value on repeated calls.

        Returns
        -------
        None
            This method does not return a value.
        """
        first = ReactorLoop._get_loop_factory()
        second = ReactorLoop._get_loop_factory()
        self.assertIs(first, second)
