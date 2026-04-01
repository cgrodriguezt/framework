from orionis.test import TestCase
from orionis.support.background.task import BackgroundTask
from orionis.support.background.tasks import BackgroundTasks

class TestBackgroundTasksInit(TestCase):

    def testInitWithoutArgumentsCreatesEmptyList(self):
        """
        Create an empty task list when no arguments are provided.

        Validates that BackgroundTasks() defaults to an empty internal
        task list without raising any errors.
        """
        bt = BackgroundTasks()
        self.assertEqual(bt.tasks, [])

    def testInitWithNoneCreatesEmptyList(self):
        """
        Create an empty task list when None is provided.

        Validates that BackgroundTasks(None) is equivalent to
        BackgroundTasks() and produces an empty list.
        """
        bt = BackgroundTasks(None)
        self.assertEqual(bt.tasks, [])

    def testInitWithSequencePopulatesList(self):
        """
        Populate the task list from a provided sequence.

        Validates that BackgroundTasks initialized with a sequence of
        BackgroundTask instances stores them as a list.
        """
        def noop(): # NOSONAR
            pass

        tasks = [BackgroundTask(noop), BackgroundTask(noop)]
        bt = BackgroundTasks(tasks)
        self.assertEqual(len(bt.tasks), 2)

    def testInitWithSequenceConvertsToList(self):
        """
        Convert the provided sequence to an internal mutable list.

        Validates that the internal representation is a list, not the
        original sequence type.
        """
        def noop(): # NOSONAR
            pass

        tasks = (BackgroundTask(noop),)
        bt = BackgroundTasks(tasks)
        self.assertIsInstance(bt.tasks, list)

    def testInitIsInstanceOfBackgroundTask(self):
        """
        Confirm BackgroundTasks is a subclass of BackgroundTask.

        Validates the inheritance relationship is correctly established
        so that polymorphic usage is supported.
        """
        bt = BackgroundTasks()
        self.assertIsInstance(bt, BackgroundTask)

    def testInitIsInstanceOfBackgroundTasks(self):
        """
        Confirm the object is an instance of BackgroundTasks itself.

        Validates that instantiation produces an object of the correct
        final type.
        """
        bt = BackgroundTasks()
        self.assertIsInstance(bt, BackgroundTasks)


class TestBackgroundTasksAddTask(TestCase):
    """Unit tests for BackgroundTasks.addTask."""

    def testAddTaskIncreasesListSize(self):
        """
        Increase the internal list size after each addTask call.

        Validates that addTask appends exactly one BackgroundTask entry
        to the internal tasks list.
        """
        bt = BackgroundTasks()
        bt.addTask(lambda: None)
        self.assertEqual(len(bt.tasks), 1)

    def testAddTaskAppendsBackgroundTaskInstance(self):
        """
        Append a BackgroundTask instance via addTask.

        Validates that the object appended by addTask is an instance of
        BackgroundTask.
        """
        bt = BackgroundTasks()
        bt.addTask(lambda: None)
        self.assertIsInstance(bt.tasks[0], BackgroundTask)

    def testAddTaskMultipleTimesAccumulates(self):
        """
        Accumulate multiple tasks after repeated addTask calls.

        Validates that calling addTask several times results in all
        tasks being stored in the list in order.
        """
        bt = BackgroundTasks()
        for _ in range(5):
            bt.addTask(lambda: None)
        self.assertEqual(len(bt.tasks), 5)

    def testAddTaskWithPositionalArgs(self):
        """
        Store positional arguments alongside the callable in addTask.

        Validates that addTask correctly wraps a function with
        positional arguments into a BackgroundTask.
        """
        bt = BackgroundTasks()
        bt.addTask(lambda a, b: a + b, 1, 2)
        self.assertEqual(len(bt.tasks), 1)

    def testAddTaskWithKeywordArgs(self):
        """
        Store keyword arguments alongside the callable in addTask.

        Validates that addTask correctly wraps a function with
        keyword arguments into a BackgroundTask.
        """
        bt = BackgroundTasks()
        bt.addTask(lambda value=0: value, value=10)
        self.assertEqual(len(bt.tasks), 1)

    def testAddTaskWithMixedArgs(self):
        """
        Store mixed positional and keyword arguments via addTask.

        Validates that addTask correctly wraps a function with both
        positional and keyword arguments into a BackgroundTask.
        """
        bt = BackgroundTasks()
        bt.addTask(lambda a, b, c=0: a + b + c, 1, 2, c=3)
        self.assertEqual(len(bt.tasks), 1)


class TestBackgroundTasksExecution(TestCase):
    """Unit tests for BackgroundTasks execution methods."""

    # ------------------------------------------------ __call__

    async def testCallRunsAllSyncTasks(self):
        """
        Execute all sync tasks when the instance is called.

        Validates that awaiting the BackgroundTasks instance runs every
        sync callable that was added.
        """
        results = []
        bt = BackgroundTasks()
        bt.addTask(lambda: results.append("a"))
        bt.addTask(lambda: results.append("b"))
        bt.addTask(lambda: results.append("c"))
        await bt()
        self.assertEqual(results, ["a", "b", "c"])

    async def testCallRunsAllAsyncTasks(self):
        """
        Execute all async tasks when the instance is called.

        Validates that awaiting the BackgroundTasks instance correctly
        awaits each async callable in the list.
        """
        results = []

        async def append(tag): # NOSONAR
            results.append(tag)

        bt = BackgroundTasks()
        bt.addTask(append, "x")
        bt.addTask(append, "y")
        await bt()
        self.assertEqual(results, ["x", "y"])

    async def testCallPreservesExecutionOrder(self):
        """
        Preserve insertion order when executing tasks.

        Validates that tasks are run sequentially in the order they
        were added, not in any other order.
        """
        order = []

        async def step(n): # NOSONAR
            order.append(n)

        bt = BackgroundTasks()
        for i in range(5):
            bt.addTask(step, i)
        await bt()
        self.assertEqual(order, [0, 1, 2, 3, 4])

    async def testCallWithEmptyListDoesNothing(self):
        """
        Complete without error when the task list is empty.

        Validates that calling a BackgroundTasks instance with no tasks
        returns normally without raising any exception.
        """
        bt = BackgroundTasks()
        await bt()

    async def testCallWithMixedSyncAndAsyncTasks(self):
        """
        Execute both sync and async tasks in a mixed list.

        Validates that BackgroundTasks correctly handles a list that
        contains both synchronous and asynchronous callables.
        """
        results = []

        async def async_append(tag): # NOSONAR
            results.append(tag)

        def sync_append(tag):
            results.append(tag)

        bt = BackgroundTasks()
        bt.addTask(async_append, "async")
        bt.addTask(sync_append, "sync")
        await bt()
        self.assertEqual(results, ["async", "sync"])

    # ------------------------------------------------ run()

    async def testRunExecutesAllTasks(self):
        """
        Execute all tasks via the run method.

        Validates that run() produces the same result as directly
        calling the BackgroundTasks instance.
        """
        results = []

        bt = BackgroundTasks()
        bt.addTask(lambda: results.append(1))
        bt.addTask(lambda: results.append(2))
        await bt.run()
        self.assertEqual(results, [1, 2])

    async def testRunEquivalentToCall(self):
        """
        Produce the same outcome from run as from direct invocation.

        Validates that run() delegates to __call__ and the behavior
        is identical for the same set of tasks.
        """
        call_results = []
        run_results = []

        async def append_to(lst, tag): # NOSONAR
            lst.append(tag)

        bt_call = BackgroundTasks()
        bt_call.addTask(append_to, call_results, "a")

        bt_run = BackgroundTasks()
        bt_run.addTask(append_to, run_results, "a")

        await bt_call()
        await bt_run.run()

        self.assertEqual(call_results, run_results)

    async def testRunWithEmptyListDoesNothing(self):
        """
        Complete without error when run is called on an empty list.

        Validates that run() on a BackgroundTasks instance with no
        registered tasks returns normally without raising any exception.
        """
        bt = BackgroundTasks()
        await bt.run()

    # ------------------------------------------------ pre-initialized tasks

    async def testCallWithPreInitializedTasks(self):
        """
        Execute tasks initialized via the constructor.

        Validates that BackgroundTask instances passed to the constructor
        are executed when the instance is called.
        """
        results = []

        async def collect(tag): # NOSONAR
            results.append(tag)

        task_a = BackgroundTask(collect, "first")
        task_b = BackgroundTask(collect, "second")
        bt = BackgroundTasks([task_a, task_b])
        await bt()
        self.assertEqual(results, ["first", "second"])

    async def testRunWithPreInitializedTasks(self):
        """
        Execute constructor-provided tasks via run.

        Validates that run() correctly processes BackgroundTask instances
        provided at construction time.
        """
        results = []

        async def collect(tag): # NOSONAR
            results.append(tag)

        bt = BackgroundTasks([BackgroundTask(collect, "only")])
        await bt.run()
        self.assertEqual(results, ["only"])

    async def testAddTaskAfterInit(self):
        """
        Allow addTask calls after initialization with a sequence.

        Validates that tasks added after construction via addTask
        are run in order after the pre-initialized tasks.
        """
        results = []

        async def collect(tag): # NOSONAR
            results.append(tag)

        bt = BackgroundTasks([BackgroundTask(collect, "first")])
        bt.addTask(collect, "second")
        await bt()
        self.assertEqual(results, ["first", "second"])
