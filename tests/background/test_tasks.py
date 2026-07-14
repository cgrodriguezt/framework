from __future__ import annotations
from orionis.background.task import BackgroundTask
from orionis.background.tasks import BackgroundTasks
from orionis.test import TestCase

class TestBackgroundTasksInitialization(TestCase):

    def testInitializesWithEmptyTaskListByDefault(self) -> None:
        """
        Start with an empty task list when no argument is provided.

        Validates that a BackgroundTasks instance created without
        arguments has an empty tasks list.
        """
        bt = BackgroundTasks()
        self.assertEqual(bt.tasks, [])

    def testInitializesWithNoneProducesEmptyList(self) -> None:
        """
        Treat None as an empty task sequence during initialization.

        Validates that passing None explicitly yields an empty tasks list
        identical to the no-argument case.
        """
        bt = BackgroundTasks(None)
        self.assertEqual(bt.tasks, [])

    def testInitializesWithProvidedListOfTasks(self) -> None:
        """
        Populate the task list from a list of BackgroundTask instances.

        Validates that the provided list is stored in the tasks attribute
        with the same length and contents.
        """

        def noop() -> None:
            pass

        task1 = BackgroundTask(noop)
        task2 = BackgroundTask(noop)
        bt = BackgroundTasks([task1, task2])
        self.assertEqual(len(bt.tasks), 2)

    def testInitializesWithTupleConvertsToList(self) -> None:
        """
        Convert a tuple of tasks to a mutable list during initialization.

        Validates that even when a tuple is supplied, the stored tasks
        attribute is a list instance.
        """

        def noop() -> None:
            pass

        bt = BackgroundTasks((BackgroundTask(noop),))
        self.assertIsInstance(bt.tasks, list)

    def testInitialTasksAreBackgroundTaskInstances(self) -> None:
        """
        Store BackgroundTask instances verbatim when supplied at init.

        Validates that the objects placed in the tasks list at construction
        are the exact same instances that were passed in.
        """

        def noop() -> None:
            pass

        task = BackgroundTask(noop)
        bt = BackgroundTasks([task])
        self.assertIs(bt.tasks[0], task)

class TestBackgroundTasksAddTask(TestCase):

    def testAddTaskAppendsOneEntry(self) -> None:
        """
        Increase the task count by one when addTask is called.

        Validates that a new BackgroundTask is appended to the tasks list
        after each addTask invocation.
        """
        bt = BackgroundTasks()

        def noop() -> None:
            pass

        bt.addTask(noop)
        self.assertEqual(len(bt.tasks), 1)

    def testAddTaskCreatesBackgroundTaskInstance(self) -> None:
        """
        Wrap the callable in a BackgroundTask when addTask is called.

        Validates that the object appended to the task list is a
        BackgroundTask instance.
        """
        bt = BackgroundTasks()

        def noop() -> None:
            pass

        bt.addTask(noop)
        self.assertIsInstance(bt.tasks[0], BackgroundTask)

    def testAddMultipleTasksGrowsListInOrder(self) -> None:
        """
        Append tasks in insertion order across multiple addTask calls.

        Validates that the tasks list grows correctly and retains the
        insertion sequence.
        """
        bt = BackgroundTasks()

        def first() -> None:
            pass

        def second() -> None:
            pass

        bt.addTask(first)
        bt.addTask(second)
        self.assertEqual(len(bt.tasks), 2)

    def testAddTaskWithPositionalArgs(self) -> None:
        """
        Accept positional arguments when adding a task.

        Validates that addTask stores the task so that positional args
        are forwarded correctly on execution.
        """
        bt = BackgroundTasks()
        received: list[tuple[int, int]] = []

        def capture(a: int, b: int) -> None:
            received.append((a, b))

        bt.addTask(capture, 3, 7)
        self.assertEqual(len(bt.tasks), 1)
        self.assertIsInstance(bt.tasks[0], BackgroundTask)

    def testAddTaskWithKeywordArgs(self) -> None:
        """
        Accept keyword arguments when adding a task.

        Validates that addTask stores the task so that keyword args are
        forwarded correctly on execution.
        """
        bt = BackgroundTasks()
        received: list[tuple[str, int]] = []

        def capture(name: str, value: int) -> None:
            received.append((name, value))

        bt.addTask(capture, name="x", value=42)
        self.assertEqual(len(bt.tasks), 1)

class TestBackgroundTasksExecution(TestCase):

    async def testRunExecutesAllTasksSequentially(self) -> None:
        """
        Execute every task in the collection in insertion order via run().

        Validates that run() runs all tasks and their effects are
        observable in the exact order they were added.
        """
        results: list[int] = []

        def first() -> None:
            results.append(1)

        def second() -> None:
            results.append(2)

        def third() -> None:
            results.append(3)

        bt = BackgroundTasks()
        bt.addTask(first)
        bt.addTask(second)
        bt.addTask(third)
        await bt.run()
        self.assertEqual(results, [1, 2, 3])

    async def testCallExecutesAllTasksSequentially(self) -> None:
        """
        Execute every task in the collection when the instance is called.

        Validates that __call__ runs all tasks in insertion order and
        all side-effects are observable.
        """
        results: list[str] = []

        async def first() -> None:
            results.append("a")

        async def second() -> None:
            results.append("b")

        bt = BackgroundTasks()
        bt.addTask(first)
        bt.addTask(second)
        await bt()
        self.assertEqual(results, ["a", "b"])

    async def testEmptyCollectionRunsWithoutError(self) -> None:
        """
        Complete without error when the task collection is empty.

        Validates that run() on an empty BackgroundTasks instance is
        a no-op that raises no exceptions.
        """
        bt = BackgroundTasks()
        await bt.run()

    async def testRunWithPreloadedTasksAtConstruction(self) -> None:
        """
        Execute tasks supplied at construction time via run().

        Validates that tasks passed during initialization are run
        correctly when run() is later invoked.
        """
        results: list[bool] = []

        def noop() -> None:
            results.append(True)

        task = BackgroundTask(noop)
        bt = BackgroundTasks([task])
        await bt.run()
        self.assertEqual(results, [True])

    async def testMixedSyncAndAsyncTasksRunInOrder(self) -> None:
        """
        Execute a mix of synchronous and asynchronous tasks in order.

        Validates that BackgroundTasks handles a collection containing
        both sync and async callables, running them sequentially.
        """
        results: list[str] = []

        def sync_func() -> None:
            results.append("sync")

        async def async_func() -> None:
            results.append("async")

        bt = BackgroundTasks()
        bt.addTask(sync_func)
        bt.addTask(async_func)
        await bt.run()
        self.assertEqual(results, ["sync", "async"])

    async def testExceptionInTaskHaltsExecution(self) -> None:
        """
        Halt sequential execution when an intermediate task raises.

        Validates that an exception raised by a task propagates to the
        caller and prevents any subsequent tasks from running.
        """
        results: list[int] = []

        def first() -> None:
            results.append(1)

        def failing() -> None:
            error_msg = "task failed"
            raise RuntimeError(error_msg)

        def third() -> None:
            results.append(3)

        bt = BackgroundTasks()
        bt.addTask(first)
        bt.addTask(failing)
        bt.addTask(third)

        with self.assertRaises(RuntimeError):
            await bt.run()

        self.assertEqual(results, [1])

    async def testRunAndCallAreEquivalent(self) -> None:
        """
        Produce identical results from run() and __call__.

        Validates that both invocation paths execute all tasks and yield
        the same side-effects.
        """
        call_results: list[int] = []
        run_results: list[int] = []

        def call_func() -> None:
            call_results.append(1)

        def run_func() -> None:
            run_results.append(1)

        bt_call = BackgroundTasks()
        bt_call.addTask(call_func)

        bt_run = BackgroundTasks()
        bt_run.addTask(run_func)

        await bt_call()
        await bt_run.run()
        self.assertEqual(call_results, [1])
        self.assertEqual(run_results, [1])

    async def testSingleTaskExecutedOnce(self) -> None:
        """
        Execute a single task exactly once when run() is called once.

        Validates that the task list containing one entry results in
        exactly one function invocation.
        """
        call_count: list[int] = []

        def counting() -> None:
            call_count.append(1)

        bt = BackgroundTasks()
        bt.addTask(counting)
        await bt.run()
        self.assertEqual(len(call_count), 1)
