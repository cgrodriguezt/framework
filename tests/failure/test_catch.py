from unittest.mock import Mock
from typing import Any, Dict
from orionis.console.kernel import KernelCLI
from orionis.console.tasks.schedule import Schedule
from orionis.failure.catch import Catch
from orionis.failure.contracts.catch import ICatch
from orionis.failure.contracts.handler import IBaseExceptionHandler
from orionis.foundation.contracts.application import IApplication
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.synchronous import SyncTestCase

class TestFailureCatch(SyncTestCase):
    """
    Comprehensive test suite for the Catch exception handler class.

    This test class validates all functionality of the Catch class including
    initialization, exception handling, integration with different kernel types,
    and proper delegation to the application's exception handler.
    """

    def setUp(self) -> None:
        """
        Set up test environment before each test method.

        Creates mock instances for dependencies and initializes test data
        used across multiple test methods. This method is called automatically
        before each test method execution.

        Notes
        -----
        The setUp method creates:
        - Mock application instance with exception handler
        - Sample exceptions for testing different scenarios
        - Mock kernel instances for CLI and Schedule testing
        """
        # Create mock application instance
        self.mock_app: Mock = Mock(spec=IApplication)

        # Create mock exception handler
        self.mock_exception_handler: Mock = Mock(spec=IBaseExceptionHandler)

        # Configure the mock application to return the exception handler
        self.mock_app.getExceptionHandler.return_value = self.mock_exception_handler

        # Create test exceptions
        self.test_exception: Exception = Exception("Test exception message")
        self.test_base_exception: BaseException = BaseException("Test base exception")

        # Create mock kernel instances
        self.mock_kernel_cli: Mock = Mock(spec=KernelCLI)
        self.mock_schedule: Mock = Mock(spec=Schedule)
        self.mock_request: Mock = Mock()

        # Create test data dictionary
        self.test_data: Dict[str, Any] = {
            "exception_message": "Test exception occurred",
            "request_data": {"command": "test", "args": []},
            "kernel_types": [KernelCLI, Schedule],
        }

    def tearDown(self) -> None:
        """
        Clean up resources after each test method completion.

        Resets all mock objects and test data to None to ensure clean state
        between test method executions and prevent test interference.
        """
        self.mock_app = None
        self.mock_exception_handler = None
        self.test_exception = None
        self.test_base_exception = None
        self.mock_kernel_cli = None
        self.mock_schedule = None
        self.mock_request = None
        self.test_data = None

    def testImplementation(self) -> None:
        """
        Tests that all methods defined in the `ICatch` interface are implemented
        by the `Catch` concrete class.

        This method uses reflection to retrieve the list of method names from both
        the interface and its concrete implementation, then asserts that each method
        in the interface exists in the implementation.

        Returns
        -------
        None
            This method does not return a value. It raises an assertion error if any
            interface method is not implemented in the concrete class.
        """
        # Retrieve the list of method names from the interface
        rf_abstract = ReflectionAbstract(ICatch).getMethods()

        # Retrieve the list of method names from the concrete implementation
        rf_concrete = ReflectionConcrete(Catch).getMethods()

        # Ensure that every method in the interface is implemented in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)

    def testInitialization(self) -> None:
        """
        Tests proper initialization of the Catch class with application dependency.

        Validates that the constructor correctly stores the application instance
        and retrieves the exception handler from the application container.
        Also verifies that the private attributes are properly set.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper initialization of the Catch instance.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Verify that the application's getExceptionHandler method was called
        self.mock_app.getExceptionHandler.assert_called_once()

        # Verify that the exception handler is stored correctly
        self.assertEqual(catch_instance._Catch__exception_handler, self.mock_exception_handler)

        # Verify that the application instance is stored correctly
        self.assertEqual(catch_instance._Catch__app, self.mock_app)

    def testExceptionWithKernelCLI(self) -> None:
        """
        Tests exception handling when kernel is an instance of KernelCLI.

        Validates that the exception method properly reports the exception
        and renders CLI output when provided with a KernelCLI kernel instance.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper exception handling with KernelCLI instances.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Call the exception method with KernelCLI kernel
        catch_instance.exception(self.mock_kernel_cli, self.mock_request, self.test_exception)

        # Verify that the exception handler's report method was called
        self.mock_app.call.assert_any_call(
            self.mock_exception_handler,
            "report",
            exception=self.test_exception,
        )

        # Verify that the exception handler's renderCLI method was called
        self.mock_app.call.assert_any_call(
            self.mock_exception_handler,
            "renderCLI",
            exception=self.test_exception,
            request=self.mock_request,
        )

        # Verify that both methods were called exactly twice total
        self.assertEqual(self.mock_app.call.call_count, 2)

    def testExceptionWithSchedule(self) -> None:
        """
        Tests exception handling when kernel is an instance of Schedule.

        Validates that the exception method properly reports the exception
        and renders CLI output when provided with a Schedule kernel instance.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper exception handling with Schedule instances.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Call the exception method with Schedule kernel
        catch_instance.exception(self.mock_schedule, self.mock_request, self.test_exception)

        # Verify that the exception handler's report method was called
        self.mock_app.call.assert_any_call(
            self.mock_exception_handler,
            "report",
            exception=self.test_exception,
        )

        # Verify that the exception handler's renderCLI method was called
        self.mock_app.call.assert_any_call(
            self.mock_exception_handler,
            "renderCLI",
            exception=self.test_exception,
            request=self.mock_request,
        )

        # Verify that both methods were called exactly twice total
        self.assertEqual(self.mock_app.call.call_count, 2)

    def testExceptionWithNonKernelType(self) -> None:
        """
        Tests exception handling when kernel is not a KernelCLI or Schedule instance.

        Validates that the exception method only reports the exception without
        rendering CLI output when provided with an unsupported kernel type.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper exception handling with unsupported kernel types.
        """
        # Create a mock kernel that is not KernelCLI or Schedule
        mock_other_kernel = Mock()

        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Call the exception method with unsupported kernel type
        catch_instance.exception(mock_other_kernel, self.mock_request, self.test_exception)

        # Verify that only the report method was called
        self.mock_app.call.assert_called_once_with(
            self.mock_exception_handler,
            "report",
            exception=self.test_exception,
        )

    def testExceptionWithNoneKernel(self) -> None:
        """
        Tests exception handling when kernel is None.

        Validates that the exception method only reports the exception without
        rendering CLI output when no kernel is provided.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper exception handling when kernel is None.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Call the exception method with None kernel
        catch_instance.exception(None, self.mock_request, self.test_exception)

        # Verify that only the report method was called
        self.mock_app.call.assert_called_once_with(
            self.mock_exception_handler,
            "report",
            exception=self.test_exception,
        )

    def testExceptionWithBaseException(self) -> None:
        """
        Tests exception handling with BaseException instead of Exception.

        Validates that the exception method properly handles BaseException
        instances, which are the parent class of all exceptions in Python.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper handling of BaseException instances.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Call the exception method with BaseException
        catch_instance.exception(self.mock_kernel_cli, self.mock_request, self.test_base_exception)

        # Verify that the exception handler's report method was called with BaseException
        self.mock_app.call.assert_any_call(
            self.mock_exception_handler,
            "report",
            exception=self.test_base_exception,
        )

        # Verify that the exception handler's renderCLI method was called with BaseException
        self.mock_app.call.assert_any_call(
            self.mock_exception_handler,
            "renderCLI",
            exception=self.test_base_exception,
            request=self.mock_request,
        )

    def testExceptionWithDifferentRequests(self) -> None:
        """
        Tests exception handling with various request types and data.

        Validates that the exception method properly passes different request
        objects to the exception handler's renderCLI method.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper handling of different request types.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Test with different request types
        test_requests = [
            {"command": "test", "args": ["--verbose"]},
            Mock(command="schedule", args=[]),
            "string_request",
            None,
            123,
        ]

        for request in test_requests:
            # Reset the mock to clear previous calls
            self.mock_app.call.reset_mock()

            # Call the exception method with different request
            catch_instance.exception(self.mock_kernel_cli, request, self.test_exception)

            # Verify that renderCLI was called with the specific request
            self.mock_app.call.assert_any_call(
                self.mock_exception_handler,
                "renderCLI",
                exception=self.test_exception,
                request=request,
            )

    def testExceptionHandlerCallOrder(self) -> None:
        """
        Tests that exception handler methods are called in the correct order.

        Validates that the report method is always called before the renderCLI
        method when handling exceptions with supported kernel types.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            the correct method call order.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Call the exception method
        catch_instance.exception(self.mock_kernel_cli, self.mock_request, self.test_exception)

        # Get the call arguments to verify order
        calls = self.mock_app.call.call_args_list

        # Verify that report was called first
        self.assertEqual(calls[0][0][1], "report")
        self.assertEqual(calls[0][1]["exception"], self.test_exception)

        # Verify that renderCLI was called second
        self.assertEqual(calls[1][0][1], "renderCLI")
        self.assertEqual(calls[1][1]["exception"], self.test_exception)
        self.assertEqual(calls[1][1]["request"], self.mock_request)

    def testMultipleExceptionHandling(self) -> None:
        """
        Tests handling multiple exceptions in sequence.

        Validates that the Catch instance can handle multiple exceptions
        correctly without state interference between calls.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper handling of multiple sequential exceptions.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Create multiple test exceptions
        exceptions = [
            Exception("First exception"),
            ValueError("Second exception"),
            RuntimeError("Third exception"),
        ]

        # Handle each exception
        for exception in exceptions:
            catch_instance.exception(self.mock_kernel_cli, self.mock_request, exception)

        # Verify that report was called for each exception
        report_calls = [call for call in self.mock_app.call.call_args_list
                       if call[0][1] == "report"]
        self.assertEqual(len(report_calls), 3)

        # Verify that renderCLI was called for each exception
        render_calls = [call for call in self.mock_app.call.call_args_list
                       if call[0][1] == "renderCLI"]
        self.assertEqual(len(render_calls), 3)

    def testExceptionHandlerIntegration(self) -> None:
        """
        Tests integration with the application's exception handler.

        Validates that the Catch class properly integrates with the application
        container and uses the correct exception handler instance.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper integration with the exception handling system.
        """
        # Create a different exception handler mock
        different_handler = Mock(spec=IBaseExceptionHandler)
        self.mock_app.getExceptionHandler.return_value = different_handler

        # Create Catch instance with the different handler
        catch_instance = Catch(self.mock_app)

        # Call the exception method
        catch_instance.exception(self.mock_kernel_cli, self.mock_request, self.test_exception)

        # Verify that the different handler was used
        self.mock_app.call.assert_any_call(
            different_handler,
            "report",
            exception=self.test_exception,
        )

        self.mock_app.call.assert_any_call(
            different_handler,
            "renderCLI",
            exception=self.test_exception,
            request=self.mock_request,
        )

    def testInstanceTypeChecking(self) -> None:
        """
        Tests that kernel type checking works correctly for different instances.

        Validates that the isinstance checks properly identify KernelCLI and
        Schedule instances versus other types of objects.

        Returns
        -------
        None
            This method does not return a value. It performs assertions to validate
            proper type checking behavior.
        """
        # Create Catch instance
        catch_instance = Catch(self.mock_app)

        # Test objects that should trigger renderCLI
        supported_kernels = [self.mock_kernel_cli, self.mock_schedule]

        # Test objects that should not trigger renderCLI
        unsupported_kernels = [Mock(), "string", 123, [], {}, None]

        # Test supported kernels
        for kernel in supported_kernels:
            self.mock_app.call.reset_mock()
            catch_instance.exception(kernel, self.mock_request, self.test_exception)

            # Should call both report and renderCLI
            self.assertEqual(self.mock_app.call.call_count, 2)

        # Test unsupported kernels
        for kernel in unsupported_kernels:
            self.mock_app.call.reset_mock()
            catch_instance.exception(kernel, self.mock_request, self.test_exception)

            # Should only call report
            self.assertEqual(self.mock_app.call.call_count, 1)
            self.mock_app.call.assert_called_once_with(
                self.mock_exception_handler,
                "report",
                exception=self.test_exception,
            )
