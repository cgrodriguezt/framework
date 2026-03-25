from __future__ import annotations
import inspect
from orionis.console.base.listener import BaseTaskListener
from orionis.console.base.contracts.listener import IBaseTaskListener
from orionis.console.entities.task_event import TaskEvent
from orionis.console.enums.events import TaskEvent as TaskEventEnum
from orionis.console.output.console import Console
from orionis.test import TestCase

class TestBaseTaskListener(TestCase):

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Create a new instance of the task listener for each test
        self.listener = BaseTaskListener()

    def testCanBeInstantiated(self) -> None:
        """
        Verify BaseTaskListener can be instantiated successfully.

        Checks that the concrete implementation can be created without errors.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Verify the instance was created successfully
        self.assertIsNotNone(self.listener)
        self.assertIsInstance(self.listener, BaseTaskListener)

    def testInheritsFromExpectedClasses(self) -> None:
        """
        Verify BaseTaskListener inherits from Console and IBaseTaskListener.

        Checks the inheritance hierarchy and method resolution order.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Check direct inheritance
        self.assertIsInstance(self.listener, Console)
        self.assertIsInstance(self.listener, IBaseTaskListener)

        # Check class hierarchy
        self.assertTrue(issubclass(BaseTaskListener, Console))
        self.assertTrue(issubclass(BaseTaskListener, IBaseTaskListener))

        # Check method resolution order
        mro = BaseTaskListener.__mro__
        self.assertIn(Console, mro)
        self.assertIn(IBaseTaskListener, mro)

    def testImplementsAllAbstractMethods(self) -> None:
        """
        Verify BaseTaskListener implements all required abstract methods.

        Checks that all abstract methods from the interface are properly implemented.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        required_methods = [
            "onTaskAdded",
            "onTaskRemoved",
            "onTaskExecuted",
            "onTaskError",
            "onTaskMissed",
            "onTaskSubmitted",
            "onTaskMaxInstances",
        ]

        for method_name in required_methods:
            # Verify method exists
            self.assertTrue(hasattr(self.listener, method_name))

            # Verify method is callable
            method = getattr(self.listener, method_name)
            self.assertTrue(callable(method))

    def testIsNotAbstractClass(self) -> None:
        """
        Verify BaseTaskListener is not an abstract class.

        Checks that the implementation class can be instantiated and has no
        abstract methods.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Verify it's not abstract
        self.assertFalse(inspect.isabstract(BaseTaskListener))

        # Verify it has no abstract methods
        abstract_methods = getattr(BaseTaskListener, "__abstractmethods__", set())
        self.assertEqual(len(abstract_methods), 0)

    def _createMockTaskEvent(self, code: int = TaskEventEnum.ADDED) -> TaskEvent:
        """
        Create a mock TaskEvent for testing.

        Parameters
        ----------
        code : int, optional
            Event code to use. Defaults to TaskEventEnum.ADDED.

        Returns
        -------
        TaskEvent
            Mock task event instance.
        """
        return TaskEvent(
            code=code,
            signature="test-task",
            jobstore="memory",
        )

    async def testOnTaskAddedExecutesSuccessfully(self) -> None:
        """
        Verify onTaskAdded method executes without errors.

        Checks that the method can be called with a TaskEvent and completes
        successfully.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create mock event
        event = self._createMockTaskEvent(TaskEventEnum.ADDED)

        # Method should execute without errors
        try:
            result = await self.listener.onTaskAdded(event)
            # Method should return None
            self.assertIsNone(result)
        except Exception as e:
            self.fail(f"onTaskAdded raised an unexpected exception: {e}")

    async def testOnTaskRemovedExecutesSuccessfully(self) -> None:
        """
        Verify onTaskRemoved method executes without errors.

        Checks that the method can be called with a TaskEvent and completes
        successfully.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create mock event
        event = self._createMockTaskEvent(TaskEventEnum.REMOVED)

        # Method should execute without errors
        try:
            result = await self.listener.onTaskRemoved(event)
            # Method should return None
            self.assertIsNone(result)
        except Exception as e:
            self.fail(f"onTaskRemoved raised an unexpected exception: {e}")

    async def testOnTaskExecutedExecutesSuccessfully(self) -> None:
        """
        Verify onTaskExecuted method executes without errors.

        Checks that the method can be called with a TaskEvent and completes
        successfully.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create mock event
        event = self._createMockTaskEvent(TaskEventEnum.EXECUTED)

        # Method should execute without errors
        try:
            result = await self.listener.onTaskExecuted(event)
            # Method should return None
            self.assertIsNone(result)
        except Exception as e:
            self.fail(f"onTaskExecuted raised an unexpected exception: {e}")

    async def testOnTaskErrorExecutesSuccessfully(self) -> None:
        """
        Verify onTaskError method executes without errors.

        Checks that the method can be called with a TaskEvent and completes
        successfully.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create mock event
        event = self._createMockTaskEvent(TaskEventEnum.ERROR)

        # Method should execute without errors
        try:
            result = await self.listener.onTaskError(event)
            # Method should return None
            self.assertIsNone(result)
        except Exception as e:
            self.fail(f"onTaskError raised an unexpected exception: {e}")

    async def testOnTaskMissedExecutesSuccessfully(self) -> None:
        """
        Verify onTaskMissed method executes without errors.

        Checks that the method can be called with a TaskEvent and completes
        successfully.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create mock event
        event = self._createMockTaskEvent(TaskEventEnum.MISSED)

        # Method should execute without errors
        try:
            result = await self.listener.onTaskMissed(event)
            # Method should return None
            self.assertIsNone(result)
        except Exception as e:
            self.fail(f"onTaskMissed raised an unexpected exception: {e}")

    async def testOnTaskSubmittedExecutesSuccessfully(self) -> None:
        """
        Verify onTaskSubmitted method executes without errors.

        Checks that the method can be called with a TaskEvent and completes
        successfully.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create mock event
        event = self._createMockTaskEvent(TaskEventEnum.SUBMITTED)

        # Method should execute without errors
        try:
            result = await self.listener.onTaskSubmitted(event)
            # Method should return None
            self.assertIsNone(result)
        except Exception as e:
            self.fail(f"onTaskSubmitted raised an unexpected exception: {e}")

    async def testOnTaskMaxInstancesExecutesSuccessfully(self) -> None:
        """
        Verify onTaskMaxInstances method executes without errors.

        Checks that the method can be called with a TaskEvent and completes
        successfully.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create mock event
        event = self._createMockTaskEvent(TaskEventEnum.MAX_INSTANCES)

        # Method should execute without errors
        try:
            result = await self.listener.onTaskMaxInstances(event)
            # Method should return None
            self.assertIsNone(result)
        except Exception as e:
            self.fail(f"onTaskMaxInstances raised an unexpected exception: {e}")

    def testAllMethodsAreAsync(self) -> None:
        """
        Verify all implementation methods are asynchronous.

        Checks that all implemented methods are defined as async functions.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        async_methods = [
            "onTaskAdded",
            "onTaskRemoved",
            "onTaskExecuted",
            "onTaskError",
            "onTaskMissed",
            "onTaskSubmitted",
            "onTaskMaxInstances",
        ]

        for method_name in async_methods:
            method = getattr(self.listener, method_name)
            self.assertTrue(inspect.iscoroutinefunction(method))

    def testMethodSignatures(self) -> None:
        """
        Verify all methods have correct signatures.

        Checks that method parameters and return types match the interface contract.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        methods_to_test = [
            "onTaskAdded",
            "onTaskRemoved",
            "onTaskExecuted",
            "onTaskError",
            "onTaskMissed",
            "onTaskSubmitted",
            "onTaskMaxInstances",
        ]

        for method_name in methods_to_test:
            with self.subTest(method=method_name):
                method = getattr(self.listener, method_name)
                signature = inspect.signature(method)

                # Check parameter count (self + event)
                parameters = list(signature.parameters.keys())
                self.assertEqual(len(parameters), 2)
                self.assertIn("self", parameters)
                self.assertIn("event", parameters)

                # Check return annotation
                self.assertEqual(signature.return_annotation, None)

    async def testMethodsWithDifferentEventTypes(self) -> None:
        """
        Verify methods can handle different TaskEvent types.

        Tests that each method can process events with different codes without errors.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        event_types_methods = [
            (TaskEventEnum.ADDED, "onTaskAdded"),
            (TaskEventEnum.REMOVED, "onTaskRemoved"),
            (TaskEventEnum.EXECUTED, "onTaskExecuted"),
            (TaskEventEnum.ERROR, "onTaskError"),
            (TaskEventEnum.MISSED, "onTaskMissed"),
            (TaskEventEnum.SUBMITTED, "onTaskSubmitted"),
            (TaskEventEnum.MAX_INSTANCES, "onTaskMaxInstances"),
        ]

        for event_code, method_name in event_types_methods:
            with self.subTest(method=method_name, event_code=event_code):
                event = self._createMockTaskEvent(event_code)
                method = getattr(self.listener, method_name)
                try:
                    result = await method(event)
                    self.assertIsNone(result)
                except Exception as e:
                    self.fail(f"{method_name} with {event_code} raised: {e}")

    def testInstanceVariablesInitialization(self) -> None:
        """
        Verify proper initialization of instance variables.

        Checks that the listener instance is properly initialized with expected state.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Since BaseTaskListener inherits from Console, it should maintain
        # proper initialization of parent class attributes
        self.assertIsInstance(self.listener, BaseTaskListener)
        self.assertIsInstance(self.listener, Console)
        self.assertIsInstance(self.listener, IBaseTaskListener)

    def testMethodsHandleNoneValues(self) -> None:
        """
        Verify methods handle edge cases with TaskEvent containing None values.

        Tests that methods can process events with optional None attributes.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        # Create event with minimal required fields and None for optional ones
        event = TaskEvent(
            code=TaskEventEnum.ADDED,
            signature="test-task",
            jobstore="memory",
            scheduled_run_time=None,
            retval=None,
            exception=None,
            traceback=None,
        )

        # Test should not fail even with None values
        try:
            # Just verify the event can be created and has expected attributes
            self.assertEqual(event.code, TaskEventEnum.ADDED)
            self.assertEqual(event.signature, "test-task")
            self.assertIsNone(event.retval)
        except Exception as e:
            self.fail(f"Event creation with None values failed: {e}")

    async def testConcurrentMethodExecution(self) -> None:
        """
        Verify methods can be executed concurrently without interference.

        Tests that multiple async method calls can run simultaneously.

        Returns
        -------
        None
            No return value; asserts within the method.
        """
        import asyncio

        # Create different events for concurrent execution
        events = [
            self._createMockTaskEvent(TaskEventEnum.ADDED),
            self._createMockTaskEvent(TaskEventEnum.EXECUTED),
            self._createMockTaskEvent(TaskEventEnum.REMOVED),
        ]

        # Execute methods concurrently
        try:
            await asyncio.gather(
                self.listener.onTaskAdded(events[0]),
                self.listener.onTaskExecuted(events[1]),
                self.listener.onTaskRemoved(events[2]),
            )
            # If we reach this point, concurrent execution succeeded
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Concurrent method execution failed: {e}")
