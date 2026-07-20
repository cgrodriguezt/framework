from __future__ import annotations
from orionis.background.task import BackgroundTask
from orionis.test import TestCase

class TestBackgroundTaskSyncExecution(TestCase):

    async def testSyncFunctionIsExecuted(self) -> None:
        """
        Execute a synchronous function when the task is awaited.

        Validates that calling a BackgroundTask wrapping a sync function
        causes the function body to run exactly once.
        """
        executed: list[bool] = []

        def sync_func() -> None:
            executed.append(True)

        task = BackgroundTask(sync_func)
        await task()
        self.assertEqual(executed, [True])

    async def testSyncFunctionReceivesPositionalArgs(self) -> None:
        """
        Forward positional arguments to the wrapped synchronous function.

        Validates that args supplied to BackgroundTask are passed through
        to the underlying callable unchanged.
        """
        received: list[tuple[int, int]] = []

        def sync_func(a: int, b: int) -> None:
            received.append((a, b))

        task = BackgroundTask(sync_func, 1, 2)
        await task()
        self.assertEqual(received, [(1, 2)])

    async def testSyncFunctionReceivesKeywordArgs(self) -> None:
        """
        Forward keyword arguments to the wrapped synchronous function.

        Validates that kwargs supplied to BackgroundTask are passed through
        to the underlying callable unchanged.
        """
        received: list[tuple[str, str]] = []

        def sync_func(x: str, y: str) -> None:
            received.append((x, y))

        task = BackgroundTask(sync_func, x="hello", y="world")
        await task()
        self.assertEqual(received, [("hello", "world")])

    async def testSyncFunctionReceivesMixedArgs(self) -> None:
        """
        Forward both positional and keyword arguments to a sync function.

        Validates that BackgroundTask correctly passes a combination of
        args and kwargs to the underlying callable.
        """
        received: list[tuple[int, int, str]] = []

        def mixed_func(a: int, b: int, c: str = "default") -> None:
            received.append((a, b, c))

        task = BackgroundTask(mixed_func, 10, 20, c="custom")
        await task()
        self.assertEqual(received, [(10, 20, "custom")])

    async def testSyncFunctionCalledExactlyOnce(self) -> None:
        """
        Invoke the wrapped synchronous function exactly once per call.

        Validates that a single await of the task results in exactly
        one invocation of the underlying callable.
        """
        call_count: list[int] = []

        def counting_func() -> None:
            call_count.append(1)

        task = BackgroundTask(counting_func)
        await task()
        self.assertEqual(len(call_count), 1)

    async def testSyncFunctionExceptionPropagates(self) -> None:
        """
        Propagate exceptions raised by a synchronous function.

        Validates that a RuntimeError raised inside the sync function
        is surfaced to the caller of the task.
        """

        def raising_func() -> None:
            error_msg = "sync error"
            raise RuntimeError(error_msg)

        task = BackgroundTask(raising_func)
        with self.assertRaises(RuntimeError):
            await task()

    async def testSyncFunctionCanBeCalledMultipleTimes(self) -> None:
        """
        Allow repeated invocations of the same task instance.

        Validates that successive awaits each invoke the wrapped sync
        function an additional time, proving the task is re-entrant.
        """
        call_count: list[int] = []

        def counting_func() -> None:
            call_count.append(1)

        task = BackgroundTask(counting_func)
        await task()
        await task()
        self.assertEqual(len(call_count), 2)

class TestBackgroundTaskAsyncExecution(TestCase):

    async def testAsyncFunctionIsExecuted(self) -> None:
        """
        Execute an asynchronous function when the task is awaited.

        Validates that a coroutine function wrapped in BackgroundTask
        is awaited and its side-effects are observable.
        """
        executed: list[bool] = []

        async def async_func() -> None:
            executed.append(True)

        task = BackgroundTask(async_func)
        await task()
        self.assertEqual(executed, [True])

    async def testAsyncFunctionReceivesPositionalArgs(self) -> None:
        """
        Forward positional arguments to the wrapped asynchronous function.

        Validates that args supplied to BackgroundTask are forwarded to
        the coroutine function unchanged.
        """
        received: list[tuple[int, int]] = []

        async def async_func(a: int, b: int) -> None:
            received.append((a, b))

        task = BackgroundTask(async_func, 1, 2)
        await task()
        self.assertEqual(received, [(1, 2)])

    async def testAsyncFunctionReceivesKeywordArgs(self) -> None:
        """
        Forward keyword arguments to the wrapped asynchronous function.

        Validates that kwargs supplied to BackgroundTask reach the
        coroutine function intact.
        """
        received: list[tuple[str, str]] = []

        async def async_func(x: str, y: str) -> None:
            received.append((x, y))

        task = BackgroundTask(async_func, x="alpha", y="beta")
        await task()
        self.assertEqual(received, [("alpha", "beta")])

    async def testAsyncFunctionCalledExactlyOnce(self) -> None:
        """
        Invoke the wrapped asynchronous function exactly once per call.

        Validates that a single await of the task results in exactly
        one invocation of the coroutine.
        """
        call_count: list[int] = []

        async def counting_func() -> None:
            call_count.append(1)

        task = BackgroundTask(counting_func)
        await task()
        self.assertEqual(len(call_count), 1)

    async def testAsyncFunctionExceptionPropagates(self) -> None:
        """
        Propagate exceptions raised by an asynchronous function.

        Validates that a ValueError raised inside the coroutine is
        surfaced to the caller of the task.
        """

        async def raising_func() -> None:
            error_msg = "async error"
            raise ValueError(error_msg)

        task = BackgroundTask(raising_func)
        with self.assertRaises(ValueError):
            await task()

    async def testAsyncFunctionCanBeCalledMultipleTimes(self) -> None:
        """
        Allow repeated invocations of the same async task instance.

        Validates that successive awaits each invoke the coroutine
        an additional time, proving the task is re-entrant.
        """
        call_count: list[int] = []

        async def counting_func() -> None:
            call_count.append(1)

        task = BackgroundTask(counting_func)
        await task()
        await task()
        self.assertEqual(len(call_count), 2)

class TestBackgroundTaskRunMethod(TestCase):

    async def testRunMethodExecutesSyncFunction(self) -> None:
        """
        Execute the wrapped sync function via the run() coroutine method.

        Validates that run() produces the same observable effect as
        awaiting the task directly via __call__.
        """
        executed: list[bool] = []

        def sync_func() -> None:
            executed.append(True)

        task = BackgroundTask(sync_func)
        await task.run()
        self.assertEqual(executed, [True])

    async def testRunMethodExecutesAsyncFunction(self) -> None:
        """
        Execute the wrapped async function via the run() coroutine method.

        Validates that run() produces the same observable effect as
        awaiting the task directly via __call__.
        """
        executed: list[bool] = []

        async def async_func() -> None:
            executed.append(True)

        task = BackgroundTask(async_func)
        await task.run()
        self.assertEqual(executed, [True])

    async def testRunMethodPropagatesException(self) -> None:
        """
        Propagate exceptions raised by the wrapped function through run().

        Validates that run() does not suppress errors thrown by the
        underlying callable.
        """

        def raising_func() -> None:
            error_msg = "run error"
            raise RuntimeError(error_msg)

        task = BackgroundTask(raising_func)
        with self.assertRaises(RuntimeError):
            await task.run()

    async def testRunAndCallAreEquivalentForSyncFunction(self) -> None:
        """
        Produce identical results from run() and __call__ for a sync func.

        Validates that both invocation paths execute the underlying
        callable and yield the same side-effects.
        """
        call_results: list[str] = []
        run_results: list[str] = []

        def call_func() -> None:
            call_results.append("called")

        def run_func() -> None:
            run_results.append("ran")

        call_task = BackgroundTask(call_func)
        run_task = BackgroundTask(run_func)
        await call_task()
        await run_task.run()
        self.assertEqual(call_results, ["called"])
        self.assertEqual(run_results, ["ran"])
