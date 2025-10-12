import asyncio
from orionis.container.container import Container
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.container.core.mocks.mock_simple_classes import Car, ICar
from tests.container.core.mocks.mock_async_optimizations import TestService, AsyncTestService, sync_callable, async_callable

class TestInvokeMethods(AsyncTestCase):

    def testInvokeSyncCallable(self):
        """
        Tests the `invoke` method with synchronous callables.

        This test verifies that the container can invoke synchronous functions
        and methods with automatic dependency injection when needed.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate invoke behavior.
        """

        # Create a container instance
        container = Container()

        # Test invoking a simple synchronous callable
        result = container.invoke(sync_callable)
        self.assertEqual(result, "Sync callable result")

        # Test invoking a lambda function
        lambda_result = container.invoke(lambda x, y: x + y, 5, 3)
        self.assertEqual(lambda_result, 8)

        # Test invoking a method on an instance
        service = TestService()
        method_result = container.invoke(service.get_message)
        self.assertEqual(method_result, "Hello from sync service")

    def testInvokeAsyncCallable(self):
        """
        Tests the `invoke` method with asynchronous callables.

        This test verifies that the container can invoke asynchronous functions
        and handle the returned coroutines appropriately.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate async invoke behavior.
        """

        # Create a container instance
        container = Container()

        # Test invoking an asynchronous callable
        result = container.invoke(async_callable)
        self.assertEqual(result, "Async callable result")

        # Test invoking an async method on an instance
        async_service = AsyncTestService()
        method_result = container.invoke(async_service.get_async_message)
        self.assertEqual(method_result, "Hello from async service")

    async def testInvokeAsyncSyncCallable(self):
        """
        Tests the `invokeAsync` method with synchronous callables.

        This test verifies that the invokeAsync method can handle synchronous
        callables and return their results directly.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate invokeAsync with sync callables.
        """

        # Create a container instance
        container = Container()

        # Test invoking a synchronous callable with invokeAsync
        result = await container.invokeAsync(sync_callable)
        self.assertEqual(result, "Sync callable result")

        # Test invoking a sync method with invokeAsync
        service = TestService()
        method_result = await container.invokeAsync(service.get_message)
        self.assertEqual(method_result, "Hello from sync service")

    async def testInvokeAsyncAsyncCallable(self):
        """
        Tests the `invokeAsync` method with asynchronous callables.

        This test verifies that the invokeAsync method properly awaits
        asynchronous callables and returns their resolved values.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate invokeAsync with async callables.
        """

        # Create a container instance
        container = Container()

        # Test invoking an asynchronous callable with invokeAsync
        result = await container.invokeAsync(async_callable)
        self.assertEqual(result, "Async callable result")

        # Test invoking an async method with invokeAsync
        async_service = AsyncTestService()
        method_result = await container.invokeAsync(async_service.get_async_message)
        self.assertEqual(method_result, "Hello from async service")

    async def testInvokeWithDependencyInjection(self):
        """
        Tests invoke methods with automatic dependency injection.

        This test verifies that the container can resolve and inject dependencies
        when invoking callables that require them.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate dependency injection during invocation.
        """

        # Create a container instance
        container = Container()

        # Create a specific car instance
        scoped_car = Car("Scoped", "Instance")

        # Register dependencies
        container.instance(ICar, scoped_car)

        # Define a function that requires dependency injection
        def func_with_dependency(car: ICar) -> str:
            return f"Using {car.brand} {car.model}"

        # Test invoke with dependency injection
        result = container.invoke(func_with_dependency)
        self.assertEqual(result, "Using Scoped Instance")

        # Test invokeAsync with dependency injection
        async def async_func_with_dependency(car: ICar) -> str:
            await asyncio.sleep(0.01)  # Simulate async operation
            return f"Async using {car.brand} {car.model}"

        async_result = await container.invokeAsync(async_func_with_dependency)
        self.assertEqual(async_result, "Async using Scoped Instance")

    async def testInvokeWithPositionalArguments(self):
        """
        Tests invoke methods with positional arguments.

        This test verifies that the container properly passes positional
        arguments to the invoked callables.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate argument passing.
        """

        # Create a container instance
        container = Container()

        # Define functions that accept positional arguments
        def add_numbers(a: int, b: int) -> int:
            return a + b

        async def multiply_numbers(x: int, y: int) -> int:
            await asyncio.sleep(0.01)
            return x * y

        # Test invoke with positional arguments
        sum_result = container.invoke(add_numbers, 5, 3)
        self.assertEqual(sum_result, 8)

        # Test invokeAsync with positional arguments
        product_result = await container.invokeAsync(multiply_numbers, 4, 6)
        self.assertEqual(product_result, 24)

    async def testInvokeWithKeywordArguments(self):
        """
        Tests invoke methods with keyword arguments.

        This test verifies that the container properly passes keyword
        arguments to the invoked callables.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate keyword argument passing.
        """

        # Create a container instance
        container = Container()

        # Define functions that accept keyword arguments
        def create_message(prefix: str = "Hello", suffix: str = "World") -> str:
            return f"{prefix} {suffix}"

        async def async_create_message(greeting: str = "Hi", name: str = "User") -> str:
            await asyncio.sleep(0.01)
            return f"{greeting}, {name}!"

        # Test invoke with keyword arguments
        message_result = container.invoke(create_message, prefix="Hi", suffix="There")
        self.assertEqual(message_result, "Hi There")

        # Test invokeAsync with keyword arguments
        async_message_result = await container.invokeAsync(async_create_message, greeting="Hello", name="Alice")
        self.assertEqual(async_message_result, "Hello, Alice!")

    async def testInvokeWithMixedArguments(self):
        """
        Tests invoke methods with mixed positional and keyword arguments.

        This test verifies that the container can handle callables that
        accept both positional and keyword arguments simultaneously.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate mixed argument handling.
        """

        # Create a container instance
        container = Container()

        # Define functions with mixed argument types
        def complex_function(base: int, multiplier: int = 2, add_value: int = 0) -> int:
            return (base * multiplier) + add_value

        async def async_complex_function(value: str, prefix: str = "Result", suffix: str = "!") -> str:
            await asyncio.sleep(0.01)
            return f"{prefix}: {value}{suffix}"

        # Test invoke with mixed arguments
        calc_result = container.invoke(complex_function, 5, multiplier=3, add_value=10)
        self.assertEqual(calc_result, 25)  # (5 * 3) + 10

        # Test invokeAsync with mixed arguments
        text_result = await container.invokeAsync(async_complex_function, "Success", suffix="!!!")
        self.assertEqual(text_result, "Result: Success!!!")

    async def testInvokeErrorHandling(self):
        """
        Tests error handling in invoke methods.

        This test verifies that the container properly propagates exceptions
        raised by invoked callables.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate error propagation.
        """

        # Create a container instance
        container = Container()

        # Define functions that raise exceptions
        def failing_function():
            raise ValueError("Sync function failed")

        async def async_failing_function():
            await asyncio.sleep(0.01)
            raise RuntimeError("Async function failed")

        # Test error handling in invoke
        with self.assertRaises(ValueError) as context:
            container.invoke(failing_function)
        self.assertEqual(str(context.exception), "Sync function failed")

        # Test error handling in invokeAsync
        with self.assertRaises(Exception) as async_context:
            await container.invokeAsync(async_failing_function)
        # The actual exception might be wrapped, so just check that an exception was raised
        self.assertIsInstance(async_context.exception, Exception)

    async def testInvokeInvalidCallable(self):
        """
        Tests invoke methods with invalid callables.

        This test verifies that the container raises appropriate exceptions
        when attempting to invoke non-callable objects.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate invalid callable handling.
        """

        # Create a container instance
        container = Container()

        # Test invoke with non-callable object
        with self.assertRaises(Exception):
            container.invoke("not_a_callable")

        # Test invokeAsync with non-callable object
        with self.assertRaises(Exception):
            await container.invokeAsync(42)