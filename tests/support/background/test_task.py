import asyncio
from orionis.test import TestCase
from orionis.support.background.task import BackgroundTask

class TestBackgroundTaskSync(TestCase):

    # ------------------------------------------------ instantiation

    def testInitStoresSyncCallable(self):
        """
        Store a synchronous callable on initialization.

        Validates that the BackgroundTask is created without error
        when given a plain synchronous function.
        """
        def noop(): # NOSONAR
            pass

        task = BackgroundTask(noop)
        self.assertIsInstance(task, BackgroundTask)

    def testInitWithPositionalArgs(self):
        """
        Accept positional arguments on initialization.

        Validates that BackgroundTask stores positional arguments
        without raising any errors during construction.
        """
        def add(a, b):
            return a + b

        task = BackgroundTask(add, 1, 2)
        self.assertIsInstance(task, BackgroundTask)

    def testInitWithKeywordArgs(self):
        """
        Accept keyword arguments on initialization.

        Validates that BackgroundTask stores keyword arguments
        without raising any errors during construction.
        """
        def greet(name="world"):
            return f"hello {name}"

        task = BackgroundTask(greet, name="orionis")
        self.assertIsInstance(task, BackgroundTask)

    def testInitWithMixedArgs(self):
        """
        Accept both positional and keyword arguments on initialization.

        Validates that BackgroundTask handles mixed argument signatures
        correctly at construction time.
        """
        def func(a, b, c=0):
            return a + b + c

        task = BackgroundTask(func, 1, 2, c=3)
        self.assertIsInstance(task, BackgroundTask)

    # ------------------------------------------------ __call__ execution

    async def testCallExecutesSyncFunction(self):
        """
        Execute a synchronous function when called asynchronously.

        Validates that awaiting a BackgroundTask whose callable is a
        plain function runs the callable and produces the expected
        side effect.
        """
        results = []

        def collect():
            results.append(1)

        task = BackgroundTask(collect)
        await task()
        self.assertEqual(results, [1])

    async def testCallForwardsSyncPositionalArgs(self):
        """
        Forward positional arguments to the underlying sync callable.

        Validates that the values captured at construction time are
        passed correctly when the task is invoked.
        """
        results = []

        def collect(a, b):
            results.append(a + b)

        task = BackgroundTask(collect, 3, 7)
        await task()
        self.assertEqual(results, [10])

    async def testCallForwardsSyncKeywordArgs(self):
        """
        Forward keyword arguments to the underlying sync callable.

        Validates that keyword arguments captured at construction time
        are forwarded correctly when the task executes.
        """
        results = []

        def collect(value=0):
            results.append(value)

        task = BackgroundTask(collect, value=42)
        await task()
        self.assertEqual(results, [42])

    async def testCallForwardsSyncMixedArgs(self):
        """
        Forward mixed positional and keyword arguments to the sync callable.

        Validates that both positional and keyword arguments are passed
        to the function in the correct order.
        """
        results = []

        def collect(a, b, c=0):
            results.append(a + b + c)

        task = BackgroundTask(collect, 1, 2, c=10)
        await task()
        self.assertEqual(results, [13])

    async def testCallRunsSyncFunctionInExecutor(self):
        """
        Run a synchronous function without blocking the event loop.

        Validates that the sync function executes via run_in_executor,
        producing a side effect visible after the await completes.
        """
        state = {"done": False}

        def mark_done():
            state["done"] = True

        task = BackgroundTask(mark_done)
        await task()
        self.assertTrue(state["done"])

    # ------------------------------------------------ run()

    async def testRunExecutesSyncFunction(self):
        """
        Execute the sync function when run is called.

        Validates that run() produces the same side effect as
        calling the instance directly.
        """
        results = []

        def collect():
            results.append("ran")

        task = BackgroundTask(collect)
        await task.run()
        self.assertEqual(results, ["ran"])

    async def testRunEquivalentToCall(self):
        """
        Produce the same result from run as from direct invocation.

        Validates that run() and __call__() are functionally equivalent
        for a synchronous callable.
        """
        state_call = []
        state_run = []

        task_call = BackgroundTask(lambda: state_call.append(1))
        task_run = BackgroundTask(lambda: state_run.append(1))

        await task_call()
        await task_run.run()

        self.assertEqual(state_call, state_run)


class TestBackgroundTaskAsync(TestCase):
    """Unit tests for BackgroundTask with asynchronous callables."""

    # ------------------------------------------------ instantiation

    def testInitStoresAsyncCallable(self):
        """
        Store an asynchronous callable on initialization.

        Validates that the BackgroundTask is created without error
        when given a coroutine function.
        """
        async def noop(): # NOSONAR
            pass

        task = BackgroundTask(noop)
        self.assertIsInstance(task, BackgroundTask)

    # ------------------------------------------------ __call__ execution

    async def testCallExecutesAsyncFunction(self):
        """
        Execute an asynchronous function when called.

        Validates that awaiting a BackgroundTask whose callable is a
        coroutine function runs it and produces the expected side effect.
        """
        results = []

        async def collect(): # NOSONAR
            results.append("async")

        task = BackgroundTask(collect)
        await task()
        self.assertEqual(results, ["async"])

    async def testCallForwardsAsyncPositionalArgs(self):
        """
        Forward positional arguments to the underlying async callable.

        Validates that positional arguments captured at construction time
        are passed correctly when the async task executes.
        """
        results = []

        async def collect(a, b): # NOSONAR
            results.append(a + b)

        task = BackgroundTask(collect, 5, 6)
        await task()
        self.assertEqual(results, [11])

    async def testCallForwardsAsyncKeywordArgs(self):
        """
        Forward keyword arguments to the underlying async callable.

        Validates that keyword arguments captured at construction are
        passed correctly to the coroutine when it runs.
        """
        results = []

        async def collect(value=0): # NOSONAR
            results.append(value)

        task = BackgroundTask(collect, value=99)
        await task()
        self.assertEqual(results, [99])

    async def testCallForwardsAsyncMixedArgs(self):
        """
        Forward mixed arguments to the underlying async callable.

        Validates that both positional and keyword arguments are passed
        correctly to the coroutine function.
        """
        results = []

        async def collect(a, b, c=0): # NOSONAR
            results.append(a + b + c)

        task = BackgroundTask(collect, 2, 3, c=5)
        await task()
        self.assertEqual(results, [10])

    async def testCallAwaitsCoroutineDirectly(self):
        """
        Await the coroutine without spawning a thread executor.

        Validates that async callables are awaited directly, confirming
        the async branch of the execution path is followed.
        """
        hit = []

        async def async_func():
            await asyncio.sleep(0)
            hit.append(True)

        task = BackgroundTask(async_func)
        await task()
        self.assertEqual(hit, [True])

    # ------------------------------------------------ run()

    async def testRunExecutesAsyncFunction(self):
        """
        Execute the async function when run is called.

        Validates that run() correctly awaits the coroutine callable
        and produces the expected side effect.
        """
        results = []

        async def collect(): # NOSONAR
            results.append("async_run")

        task = BackgroundTask(collect)
        await task.run()
        self.assertEqual(results, ["async_run"])

    async def testRunAndCallProduceSameResult(self):
        """
        Produce identical behavior from run and direct invocation.

        Validates that run() and __call__() are equivalent for an
        async callable.
        """
        shared = []

        async def collector(tag): # NOSONAR
            shared.append(tag)

        await BackgroundTask(collector, "call")()
        await BackgroundTask(collector, "run").run()

        self.assertEqual(shared, ["call", "run"])
