
import asyncio
from unittest.mock import Mock, patch
from orionis.services.asynchrony.coroutines import Coroutine
from orionis.services.asynchrony.exceptions import OrionisCoroutineException
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.test.cases.synchronous import SyncTestCase

class TestServicesAsynchronyCoroutine(AsyncTestCase):

    async def testExecuteWithActiveEventLoop(self):
        """
        Tests coroutine execution within an active event loop.

        This method verifies that a coroutine can be executed successfully when an event loop is already running,
        such as in asynchronous environments (e.g., Jupyter notebooks or ASGI applications). It ensures that the
        Coroutine wrapper correctly awaits and returns the result of the coroutine.

        Returns
        -------
        None
            This is a test method and does not return a value. It asserts that the coroutine result matches the expected output.
        """

        # Simple coroutine that returns a string
        async def sample_coroutine():
            await asyncio.sleep(0.1)
            return "Hello, World!"

        # Await the result of running the coroutine using the Coroutine wrapper
        result = await Coroutine(sample_coroutine()).run()

        # Assert that the result matches the expected output
        self.assertEqual(result, "Hello, World!")

    def testExecuteWithoutActiveEventLoop(self):
        """
        Tests coroutine execution without an active event loop.

        This method simulates the scenario where a coroutine is executed in a synchronous context,
        such as a standard Python script, where no event loop is running. It verifies that the
        Coroutine wrapper can correctly create and manage an event loop internally, execute the
        coroutine, and return the expected result.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the coroutine result matches the expected output.
        """

        # Define a simple coroutine that returns a string
        async def sample_coroutine():
            await asyncio.sleep(0.1)
            return "Hello, World!"

        # Run the coroutine using the Coroutine wrapper, which should handle event loop creation
        result = Coroutine(sample_coroutine()).run()

        # Assert that the result matches the expected output
        self.assertEqual(result, "Hello, World!")

    def testExecuteWithNonCoroutine(self):
        """
        Tests execution of a non-coroutine object.

        This method verifies that passing a non-coroutine object to the Coroutine wrapper
        raises an OrionisCoroutineException. It ensures that the Coroutine class enforces
        the requirement for coroutine objects and does not accept regular functions or other types.

        Parameters
        ----------
        self : TestServicesAsynchronyCoroutine
            The test case instance.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the appropriate exception is raised.
        """

        # Define a regular function (not a coroutine)
        def sample_no_coroutine():
            return "Hello, World!"

        # Assert that passing a non-coroutine raises OrionisCoroutineException
        with self.assertRaises(OrionisCoroutineException):
            Coroutine(sample_no_coroutine()).run()

    async def testInvokeCoroutineFunctionWithActiveEventLoop(self):
        """
        Tests invoke method with a coroutine function in an active event loop.

        This method verifies that the invoke method can correctly handle coroutine functions
        when called within an active event loop context. It ensures that the coroutine function
        is properly scheduled and returns a Task object that can be awaited for the result.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the coroutine function
            is correctly invoked and returns the expected result.
        """

        # Define a coroutine function that accepts arguments
        async def sample_coroutine_func(message, multiplier=1):
            await asyncio.sleep(0.1)
            return message * multiplier

        # Create a Coroutine wrapper with the coroutine function
        coroutine_wrapper = Coroutine(sample_coroutine_func)

        # Invoke the coroutine function with arguments
        result = coroutine_wrapper.invoke("Hello!", multiplier=2)

        # Verify that the result is a Task (scheduled for execution)
        self.assertIsInstance(result, asyncio.Task)

        # Await the Task to get the actual result
        actual_result = await result
        self.assertEqual(actual_result, "Hello!Hello!")

    def testInvokeCoroutineFunctionWithoutActiveEventLoop(self):
        """
        Tests invoke method with a coroutine function without an active event loop.

        This method simulates invoking a coroutine function in a synchronous context where
        no event loop is running. It verifies that the Coroutine wrapper can execute the
        coroutine function synchronously using asyncio.run and return the expected result.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the coroutine function
            is correctly executed synchronously and returns the expected result.
        """

        # Define a coroutine function that accepts arguments
        async def sample_coroutine_func(message, suffix="!"):
            await asyncio.sleep(0.1)
            return f"{message}{suffix}"

        # Create a Coroutine wrapper and invoke the function
        result = Coroutine(sample_coroutine_func).invoke("Hello", suffix=" World!")

        # Assert that the result matches the expected output
        self.assertEqual(result, "Hello World!")

    def testInvokeRegularCallable(self):
        """
        Tests invoke method with a regular (non-coroutine) callable function.

        This method verifies that the invoke method can handle regular Python functions
        that are not coroutines. It ensures that such functions are executed directly
        and their results are returned without any asynchronous processing.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the regular function
            is correctly invoked and returns the expected result.
        """

        # Define a regular function that accepts arguments
        def regular_function(x, y=10):
            return x + y

        # Create a Coroutine wrapper and invoke the regular function
        result = Coroutine(regular_function).invoke(5, y=15)

        # Assert that the result matches the expected output
        self.assertEqual(result, 20)

    def testInvokeWithNonCallableObject(self):
        """
        Tests invoke method with a non-callable object.

        This method verifies that attempting to invoke a non-callable object raises
        an OrionisCoroutineException. It ensures that the Coroutine wrapper properly
        validates that the wrapped object is callable before attempting invocation.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the appropriate
            exception is raised when trying to invoke a non-callable object.
        """

        # Create a non-callable object
        non_callable_object = "This is a string, not a callable"

        # Create a Coroutine wrapper with the non-callable object
        coroutine_wrapper = Coroutine(non_callable_object)

        # Assert that invoking a non-callable raises OrionisCoroutineException
        with self.assertRaises(OrionisCoroutineException) as context:
            coroutine_wrapper.invoke()

        # Verify the exception message contains appropriate information
        self.assertIn("Cannot invoke non-callable object", str(context.exception))

    def testInvokeCoroutineFunctionException(self):
        """
        Tests invoke method exception handling with a coroutine function.

        This method verifies that exceptions raised within coroutine functions during
        invocation are properly caught and wrapped in an OrionisCoroutineException.
        It ensures that error context is preserved and debugging information is available.

        Returns
        -------
        None
            This test method does not return a value. It asserts that exceptions are
            properly wrapped and contain appropriate error information.
        """

        # Define a coroutine function that raises an exception
        async def failing_coroutine():
            await asyncio.sleep(0.1)
            raise ValueError("Test exception from coroutine")

        # Create a Coroutine wrapper
        coroutine_wrapper = Coroutine(failing_coroutine)

        # Test exception handling in synchronous context (no active loop)
        with patch('asyncio.get_running_loop', side_effect=RuntimeError("No running loop")):
            with self.assertRaises(OrionisCoroutineException) as context:
                coroutine_wrapper.invoke()

            # Verify the exception contains appropriate error information
            self.assertIn("Failed to execute coroutine synchronously", str(context.exception))

    def testInvokeRegularCallableException(self):
        """
        Tests invoke method exception handling with a regular callable.

        This method verifies that exceptions raised within regular (non-coroutine) functions
        during invocation are properly caught and wrapped in a RuntimeError. It ensures that
        the error handling distinguishes between coroutine and non-coroutine exceptions.

        Returns
        -------
        None
            This test method does not return a value. It asserts that exceptions from
            regular callables are properly wrapped with appropriate error information.
        """

        # Define a regular function that raises an exception
        def failing_function():
            raise ValueError("Test exception from regular function")

        # Create a Coroutine wrapper and test exception handling
        with self.assertRaises(RuntimeError) as context:
            Coroutine(failing_function).invoke()

        # Verify the exception contains appropriate error information
        self.assertIn("Unexpected error during callable invocation", str(context.exception))

    def testRunWithCoroutineObject(self):
        """
        Tests run method with a coroutine object without an active event loop.

        This method verifies that the run method can execute a coroutine object
        synchronously when no event loop is active. It ensures that the coroutine
        is properly executed and its result is returned.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the coroutine
            object is correctly executed and returns the expected result.
        """

        # Define a coroutine function and create a coroutine object
        async def sample_coroutine():
            await asyncio.sleep(0.1)
            return "Coroutine executed successfully"

        coroutine_obj = sample_coroutine()

        # Run the coroutine object using the Coroutine wrapper
        result = Coroutine(coroutine_obj).run()

        # Assert that the result matches the expected output
        self.assertEqual(result, "Coroutine executed successfully")

    async def testRunWithCoroutineObjectInActiveLoop(self):
        """
        Tests run method with a coroutine object in an active event loop.

        This method verifies that when run is called within an active event loop,
        the coroutine object is scheduled for asynchronous execution and returns
        a Future that can be awaited for the result.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the coroutine
            object is correctly scheduled and returns the expected result.
        """

        # Define a coroutine function and create a coroutine object
        async def sample_coroutine():
            await asyncio.sleep(0.1)
            return "Async execution successful"

        coroutine_obj = sample_coroutine()

        # Run the coroutine object using the Coroutine wrapper (within active loop)
        future_result = Coroutine(coroutine_obj).run()

        # Verify that the result is a Future
        self.assertIsInstance(future_result, asyncio.Future)

        # Await the Future to get the actual result
        actual_result = await future_result
        self.assertEqual(actual_result, "Async execution successful")

    def testRunWithNonCoroutineObjectRaisesException(self):
        """
        Tests run method with a non-coroutine object raises appropriate exception.

        This method verifies that attempting to run a non-coroutine object with
        the run method raises an OrionisCoroutineException. It ensures that the
        Coroutine wrapper properly validates the object type before execution.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the appropriate
            exception is raised when trying to run a non-coroutine object.
        """

        # Define a regular function (not a coroutine)
        def regular_function():
            return "This is not a coroutine"

        # Assert that running a non-coroutine raises OrionisCoroutineException
        with self.assertRaises(OrionisCoroutineException) as context:
            Coroutine(regular_function).run()

        # Verify the exception message contains appropriate information
        self.assertIn("Expected a coroutine object", str(context.exception))

    def testInvokeWithEmptyArguments(self):
        """
        Tests invoke method with empty arguments on various callable types.

        This method verifies that the invoke method correctly handles cases where
        no arguments are provided to both coroutine functions and regular callables.
        It ensures that functions that don't require arguments can be invoked properly.

        Returns
        -------
        None
            This test method does not return a value. It asserts that functions
            without parameters are correctly invoked.
        """

        # Test with regular function that takes no arguments
        def no_args_function():
            return "No arguments needed"

        result = Coroutine(no_args_function).invoke()
        self.assertEqual(result, "No arguments needed")

        # Test with coroutine function that takes no arguments (synchronous execution)
        async def no_args_coroutine():
            await asyncio.sleep(0.1)
            return "Async no arguments"

        with patch('asyncio.get_running_loop', side_effect=RuntimeError("No running loop")):
            result = Coroutine(no_args_coroutine).invoke()
            self.assertEqual(result, "Async no arguments")

    def testInvokeWithKeywordOnlyArguments(self):
        """
        Tests invoke method with keyword-only arguments.

        This method verifies that the invoke method correctly passes keyword-only
        arguments to both coroutine functions and regular callables. It ensures
        that complex argument patterns are handled properly.

        Returns
        -------
        None
            This test method does not return a value. It asserts that keyword-only
            arguments are correctly passed and processed.
        """

        # Test with regular function that uses keyword-only arguments
        def keyword_only_function(*, name, age=25):
            return f"{name} is {age} years old"

        result = Coroutine(keyword_only_function).invoke(name="Alice", age=30)
        self.assertEqual(result, "Alice is 30 years old")

        # Test with coroutine function that uses keyword-only arguments
        async def keyword_only_coroutine(*, message, repeat=1):
            await asyncio.sleep(0.1)
            return message * repeat

        with patch('asyncio.get_running_loop', side_effect=RuntimeError("No running loop")):
            result = Coroutine(keyword_only_coroutine).invoke(message="Test", repeat=3)
            self.assertEqual(result, "TestTestTest")


class TestServicesAsynchronyCoroutineSynchronous(SyncTestCase):
    """
    Synchronous test cases for the Coroutine class.

    This test class contains synchronous test methods that test the Coroutine class
    functionality in environments without active event loops. These tests inherit
    from SyncTestCase to ensure proper synchronous test execution context.
    """

    def testInitializationWithCoroutineFunction(self):
        """
        Tests Coroutine initialization with a coroutine function.

        This method verifies that a Coroutine object can be properly initialized
        with a coroutine function. It ensures that the wrapper stores the function
        correctly without executing it during initialization.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the Coroutine
            object is properly initialized and ready for execution.
        """

        # Define a coroutine function
        async def sample_coroutine():
            await asyncio.sleep(0.01)
            return "Test message"

        # Initialize Coroutine wrapper
        coroutine_wrapper = Coroutine(sample_coroutine)

        # Verify that the wrapper is created without errors
        self.assertIsInstance(coroutine_wrapper, Coroutine)

    def testInitializationWithCoroutineObject(self):
        """
        Tests Coroutine initialization with a coroutine object.

        This method verifies that a Coroutine object can be properly initialized
        with an already created coroutine object. It ensures that the wrapper
        accepts pre-created coroutine objects for later execution.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the Coroutine
            object is properly initialized with a coroutine object.
        """

        # Define a coroutine function and create a coroutine object
        async def sample_coroutine():
            await asyncio.sleep(0.01)
            return "Test message"

        coroutine_obj = sample_coroutine()

        try:
            # Initialize Coroutine wrapper with coroutine object
            coroutine_wrapper = Coroutine(coroutine_obj)

            # Verify that the wrapper is created without errors
            self.assertIsInstance(coroutine_wrapper, Coroutine)
        finally:
            # Ensure the coroutine object is properly closed to avoid warnings
            coroutine_obj.close()

    def testInitializationWithRegularCallable(self):
        """
        Tests Coroutine initialization with a regular callable function.

        This method verifies that a Coroutine object can be initialized with
        regular (non-coroutine) callable functions. It ensures that the wrapper
        can handle mixed callable types for flexible usage patterns.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the Coroutine
            object is properly initialized with a regular callable.
        """

        # Define a regular function
        def regular_function():
            return "Regular function result"

        # Initialize Coroutine wrapper with regular function
        coroutine_wrapper = Coroutine(regular_function)

        # Verify that the wrapper is created without errors
        self.assertIsInstance(coroutine_wrapper, Coroutine)

    def testInitializationWithNonCallableObject(self):
        """
        Tests Coroutine initialization with a non-callable object.

        This method verifies that a Coroutine object can be initialized with
        non-callable objects without immediate validation. The validation occurs
        during invocation rather than initialization, allowing for flexible
        initialization patterns.

        Returns
        -------
        None
            This test method does not return a value. It asserts that the Coroutine
            object is properly initialized even with non-callable objects.
        """

        # Create a non-callable object
        non_callable = {"key": "value"}

        # Initialize Coroutine wrapper (should not raise exception during init)
        coroutine_wrapper = Coroutine(non_callable)

        # Verify that the wrapper is created without errors
        self.assertIsInstance(coroutine_wrapper, Coroutine)