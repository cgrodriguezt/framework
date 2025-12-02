import inspect
from unittest.mock import Mock, patch
from orionis.services.introspection.callables.reflection import ReflectionCallable
from orionis.services.introspection.exceptions import (
    ReflectionAttributeError,
    ReflectionTypeError
)
from orionis.services.introspection.dependencies.entities.signature import SignatureArguments
from orionis.test.cases.synchronous import SyncTestCase

class TestReflectionCallable(SyncTestCase):
    """
    Test suite for the ReflectionCallable class.

    This class provides comprehensive testing coverage for all functionality
    of the ReflectionCallable class, including constructor validation,
    method introspection, dependency analysis, and execution patterns for
    both synchronous and asynchronous callables.

    Notes
    -----
    Uses SyncTestCase as the base class since all test methods are synchronous,
    even when testing asynchronous callable handling.
    """

    def setUp(self) -> None: # NOSONAR
        """
        Initialize test fixtures and sample callables for testing.

        Creates various types of callable objects to test different scenarios:
        - Regular functions with and without parameters
        - Lambda functions
        - Methods with default parameters
        - Async functions
        - Functions with docstrings
        """
        # Regular function without parameters
        def sample_function():
            """Sample function for testing."""
            return "test_result"

        # Function with parameters and defaults
        def function_with_params(a: int, b: str = "default", c=None):
            """Function with mixed parameters."""
            return f"{a}-{b}-{c}"

        # Lambda function
        self.lambda_func = lambda x: x * 2

        # Async function
        async def async_function(param: str = "async_default"): # NOSONAR
            """Async function for testing."""
            return f"async_{param}"

        # Function without docstring
        def function_no_doc():
            return "no_doc"

        # Store test callables
        self.sample_function = sample_function
        self.function_with_params = function_with_params
        self.async_function = async_function
        self.function_no_doc = function_no_doc

        # Create ReflectionCallable instances
        self.reflection_callable = ReflectionCallable(self.sample_function)
        self.reflection_with_params = ReflectionCallable(self.function_with_params)
        self.reflection_lambda = ReflectionCallable(self.lambda_func)
        self.reflection_async = ReflectionCallable(self.async_function)
        self.reflection_no_doc = ReflectionCallable(self.function_no_doc)

    def tearDown(self) -> None: # NOSONAR
        """
        Clean up test fixtures after each test.

        Resets all callable references and ReflectionCallable instances
        to ensure clean state between tests. Also properly closes any
        potential coroutine objects that may have been created during testing.
        """
        # Close any potential coroutine objects that may have been inadvertently created
        import gc
        import inspect

        # Collect any unclosed coroutines and close them
        for obj in gc.get_objects():
            if inspect.iscoroutine(obj):
                obj.close()

        # Clean up all references
        self.sample_function = None
        self.function_with_params = None
        self.lambda_func = None
        self.async_function = None
        self.function_no_doc = None
        self.reflection_callable = None
        self.reflection_with_params = None
        self.reflection_lambda = None
        self.reflection_async = None
        self.reflection_no_doc = None

    def testConstructorWithValidFunction(self) -> None:
        """
        Test constructor accepts valid function types.

        Validates that the ReflectionCallable constructor correctly accepts
        and initializes with various types of valid callable objects including
        regular functions, methods, and lambdas.

        Raises
        ------
        AssertionError
            If constructor fails to accept valid callable types or if
            initialization doesn't preserve the original callable.
        """
        # Test with regular function
        reflection = ReflectionCallable(self.sample_function)
        self.assertEqual(reflection.getCallable(), self.sample_function)

        # Test with lambda
        reflection_lambda = ReflectionCallable(self.lambda_func)
        self.assertEqual(reflection_lambda.getCallable(), self.lambda_func)

        # Test with async function
        reflection_async = ReflectionCallable(self.async_function)
        self.assertEqual(reflection_async.getCallable(), self.async_function)

    def testConstructorWithInvalidCallable(self) -> None:
        """
        Test constructor rejects invalid callable types.

        Validates that the constructor raises ReflectionTypeError when
        provided with non-callable objects or callables without the
        required introspection attributes.

        Raises
        ------
        AssertionError
            If constructor fails to reject invalid types or raises
            incorrect exception types.
        """
        # Test with non-callable objects
        invalid_objects = [
            "not_callable",
            123,
            [],
            {},
            None,
            object()
        ]

        for invalid_obj in invalid_objects:
            with self.assertRaises(ReflectionTypeError):
                ReflectionCallable(invalid_obj)

        # Test with built-in function (lacks __code__ attribute)
        with self.assertRaises(ReflectionTypeError):
            ReflectionCallable(len)

    def testGetCallable(self) -> None:
        """
        Test getCallable method returns the wrapped function.

        Validates that getCallable correctly returns the original callable
        object that was passed to the constructor without modification.

        Raises
        ------
        AssertionError
            If getCallable returns incorrect callable or modifies the
            original function reference.
        """
        self.assertEqual(self.reflection_callable.getCallable(), self.sample_function)
        self.assertEqual(self.reflection_with_params.getCallable(), self.function_with_params)
        self.assertEqual(self.reflection_lambda.getCallable(), self.lambda_func)

    def testGetName(self) -> None:
        """
        Test getName method returns correct function names.

        Validates that getName returns the proper name for different types
        of callables including regular functions, lambdas, and async functions.

        Raises
        ------
        AssertionError
            If getName returns incorrect function names or fails to handle
            different callable types properly.
        """
        self.assertEqual(self.reflection_callable.getName(), "sample_function")
        self.assertEqual(self.reflection_with_params.getName(), "function_with_params")
        self.assertEqual(self.reflection_lambda.getName(), "<lambda>")
        self.assertEqual(self.reflection_async.getName(), "async_function")

    def testGetModuleName(self) -> None:
        """
        Test getModuleName method returns correct module names.

        Validates that getModuleName correctly identifies the module where
        each callable is defined, handling both regular functions and lambdas.

        Raises
        ------
        AssertionError
            If getModuleName returns incorrect module names or fails to
            properly identify the defining module.
        """
        expected_module = self.__class__.__module__
        self.assertEqual(self.reflection_callable.getModuleName(), expected_module)
        self.assertEqual(self.reflection_with_params.getModuleName(), expected_module)
        self.assertEqual(self.reflection_lambda.getModuleName(), expected_module)

    def testGetModuleWithCallableName(self) -> None:
        """
        Test getModuleWithCallableName method returns fully qualified names.

        Validates that the method correctly combines module name and callable
        name to create proper fully qualified identifiers for different
        types of callables.

        Raises
        ------
        AssertionError
            If getModuleWithCallableName fails to create correct fully
            qualified names or handles different callable types improperly.
        """
        expected_module = self.__class__.__module__
        expected_fqn = f"{expected_module}.sample_function"
        self.assertEqual(self.reflection_callable.getModuleWithCallableName(), expected_fqn)

        expected_lambda_fqn = f"{expected_module}.<lambda>"
        self.assertEqual(self.reflection_lambda.getModuleWithCallableName(), expected_lambda_fqn)

    def testGetDocstring(self) -> None:
        """
        Test getDocstring method returns correct docstrings.

        Validates that getDocstring properly retrieves docstrings from
        callables that have them and returns empty strings for callables
        without docstrings.

        Raises
        ------
        AssertionError
            If getDocstring fails to retrieve correct docstrings or
            doesn't handle missing docstrings properly.
        """
        # Test function with docstring
        self.assertEqual(self.reflection_callable.getDocstring(), "Sample function for testing.")
        self.assertEqual(self.reflection_with_params.getDocstring(), "Function with mixed parameters.")

        # Test function without docstring
        self.assertEqual(self.reflection_no_doc.getDocstring(), "")

        # Test lambda (typically no docstring)
        self.assertEqual(self.reflection_lambda.getDocstring(), "")

    def testGetSourceCode(self) -> None:
        """
        Test getSourceCode method retrieves function source code.

        Validates that getSourceCode correctly uses Python's inspect module
        to retrieve the complete source code of wrapped callables.

        Raises
        ------
        AssertionError
            If getSourceCode fails to retrieve source code or returns
            incorrect source code content.
        """
        source_code = self.reflection_callable.getSourceCode()
        self.assertIn("def sample_function():", source_code)
        self.assertIn("return \"test_result\"", source_code)

        # Test with function with parameters
        param_source = self.reflection_with_params.getSourceCode()
        self.assertIn("def function_with_params(a: int, b: str = \"default\", c=None):", param_source)

    @patch('inspect.getsource')
    def testGetSourceCodeRaisesReflectionAttributeError(self, mock_getsource) -> None:
        """
        Test getSourceCode raises ReflectionAttributeError on OSError.

        Validates that when inspect.getsource raises an OSError (e.g., for
        built-in functions or functions without accessible source), the method
        properly converts it to a ReflectionAttributeError.

        Parameters
        ----------
        mock_getsource : MagicMock
            Mocked inspect.getsource function that will raise OSError.

        Raises
        ------
        AssertionError
            If getSourceCode doesn't properly convert OSError to
            ReflectionAttributeError or exception message is incorrect.
        """
        mock_getsource.side_effect = OSError("Source not available")

        with self.assertRaises(ReflectionAttributeError) as context:
            self.reflection_callable.getSourceCode()

        self.assertIn("Could not retrieve source code", str(context.exception))

    def testGetFile(self) -> None:
        """
        Test getFile method returns correct source file paths.

        Validates that getFile correctly uses inspect.getfile to retrieve
        the absolute path to the source file containing the callable.

        Raises
        ------
        AssertionError
            If getFile returns incorrect file paths or fails to handle
            different callable types properly.
        """
        file_path = self.reflection_callable.getFile()
        self.assertTrue(file_path.endswith("test_reflection_callable.py"))

        # Test with different callables from same file
        param_file = self.reflection_with_params.getFile()
        self.assertEqual(file_path, param_file)

    def testGetFileRaisesTypeErrorForBuiltins(self) -> None:
        """
        Test getFile raises TypeError for built-in functions.

        Validates that getFile properly propagates TypeError when called
        on built-in functions or other callables without accessible source files.

        Raises
        ------
        AssertionError
            If getFile doesn't raise TypeError for built-in functions or
            if the exception handling is incorrect.
        """
        # This test would fail during construction, so we mock the scenario
        with patch('inspect.getfile') as mock_getfile:
            mock_getfile.side_effect = TypeError("Built-in function")
            with self.assertRaises(TypeError):
                self.reflection_callable.getFile()

    def testCallSynchronousFunction(self) -> None:
        """
        Test call method executes synchronous functions correctly.

        Validates that the call method properly executes synchronous callables
        with various argument combinations and returns correct results.

        Raises
        ------
        AssertionError
            If call method fails to execute synchronous functions correctly
            or returns incorrect results.
        """
        # Test function without parameters
        result = self.reflection_callable.call()
        self.assertEqual(result, "test_result")

        # Test function with parameters
        result_with_params = self.reflection_with_params.call(42, "custom", "extra")
        self.assertEqual(result_with_params, "42-custom-extra")

        # Test with default parameters
        result_defaults = self.reflection_with_params.call(99)
        self.assertEqual(result_defaults, "99-default-None")

        # Test lambda
        lambda_result = self.reflection_lambda.call(5)
        self.assertEqual(lambda_result, 10)

    @patch('orionis.services.introspection.callables.reflection.Coroutine')
    def testCallAsynchronousFunction(self, mock_coroutine_class) -> None:
        """
        Test call method handles asynchronous functions correctly.

        Validates that the call method detects coroutine functions and
        properly delegates execution to the Coroutine wrapper class
        for async execution management.

        Parameters
        ----------
        mock_coroutine_class : MagicMock
            Mocked Coroutine class to verify async function handling.

        Raises
        ------
        AssertionError
            If call method fails to detect async functions or doesn't
            properly delegate to Coroutine wrapper.
        """
        # Setup mock coroutine instance
        mock_coroutine_instance = Mock()
        mock_coroutine_instance.run.return_value = "async_test_result"
        mock_coroutine_class.return_value = mock_coroutine_instance

        # Call async function
        result = self.reflection_async.call("test_param")

        # Verify Coroutine was instantiated and run was called
        mock_coroutine_class.assert_called_once()
        mock_coroutine_instance.run.assert_called_once()
        self.assertEqual(result, "async_test_result")

    def testGetSignature(self) -> None:
        """
        Test getSignature method returns correct inspect.Signature objects.

        Validates that getSignature properly uses inspect.signature to
        retrieve comprehensive signature information including parameter
        names, defaults, and type annotations.

        Raises
        ------
        AssertionError
            If getSignature returns incorrect signature objects or fails
            to handle different parameter configurations properly.
        """
        # Test simple function signature
        signature = self.reflection_callable.getSignature()
        self.assertIsInstance(signature, inspect.Signature)
        self.assertEqual(len(signature.parameters), 0)

        # Test function with parameters
        param_signature = self.reflection_with_params.getSignature()
        self.assertEqual(len(param_signature.parameters), 3)

        params = list(param_signature.parameters.keys())
        self.assertEqual(params, ['a', 'b', 'c'])

        # Check parameter defaults
        b_param = param_signature.parameters['b']
        self.assertEqual(b_param.default, "default")

        # Check type annotations
        a_param = param_signature.parameters['a']
        self.assertEqual(a_param.annotation, int)

    @patch('orionis.services.introspection.callables.reflection.ReflectDependencies')
    def testGetDependencies(self, mock_reflect_dependencies_class) -> None:
        """
        Test getDependencies method analyzes callable dependencies correctly.

        Validates that getDependencies properly instantiates ReflectDependencies
        and calls getCallableDependencies to analyze the callable's parameter
        dependencies for injection purposes.

        Parameters
        ----------
        mock_reflect_dependencies_class : MagicMock
            Mocked ReflectDependencies class to verify dependency analysis.

        Raises
        ------
        AssertionError
            If getDependencies doesn't properly instantiate ReflectDependencies
            or call the correct analysis method.
        """
        # Setup mock dependency analyzer
        mock_analyzer_instance = Mock()
        mock_resolve_args = Mock(spec=SignatureArguments)
        mock_analyzer_instance.getCallableDependencies.return_value = mock_resolve_args
        mock_reflect_dependencies_class.return_value = mock_analyzer_instance

        # Call getDependencies
        result = self.reflection_callable.getDependencies()

        # Verify ReflectDependencies was instantiated with correct callable
        mock_reflect_dependencies_class.assert_called_once_with(self.sample_function)

        # Verify getCallableDependencies was called
        mock_analyzer_instance.getCallableDependencies.assert_called_once()

        # Verify correct return value
        self.assertEqual(result, mock_resolve_args)

    def testIntegrationWithRealDependencyAnalysis(self) -> None:
        """
        Test getDependencies integration with real ReflectDependencies.

        Validates that getDependencies works correctly with the actual
        ReflectDependencies implementation without mocking, ensuring
        proper integration between components.

        Raises
        ------
        AssertionError
            If getDependencies integration fails or returns incorrect
            dependency analysis results.
        """
        # Test with function that has parameters
        dependencies = self.reflection_with_params.getDependencies()
        self.assertIsInstance(dependencies, SignatureArguments)

        # Verify the dependencies object has the expected structure
        self.assertTrue(hasattr(dependencies, 'resolved'))
        self.assertTrue(hasattr(dependencies, 'unresolved'))
        self.assertTrue(hasattr(dependencies, 'ordered'))

    def testCallWithExceptionPropagation(self) -> None:
        """
        Test call method properly propagates exceptions from wrapped functions.

        Validates that when a wrapped function raises an exception, the call
        method allows the exception to propagate unchanged rather than
        catching or modifying it.

        Raises
        ------
        AssertionError
            If call method doesn't properly propagate exceptions or
            modifies exception behavior.
        """
        def function_that_raises():
            raise ValueError("Test exception")

        reflection_error = ReflectionCallable(function_that_raises)

        with self.assertRaises(ValueError) as context:
            reflection_error.call()

        self.assertEqual(str(context.exception), "Test exception")

    def testCallWithKeywordArguments(self) -> None:
        """
        Test call method handles keyword arguments correctly.

        Validates that the call method properly passes both positional
        and keyword arguments to the wrapped callable and maintains
        argument order and naming.

        Raises
        ------
        AssertionError
            If call method fails to handle keyword arguments correctly
            or doesn't maintain proper argument passing semantics.
        """
        # Test with mixed positional and keyword arguments
        result = self.reflection_with_params.call(1, c="keyword_value")
        self.assertEqual(result, "1-default-keyword_value")

        # Test with all keyword arguments
        result_all_kwargs = self.reflection_with_params.call(a=100, b="all_kwargs", c=True)
        self.assertEqual(result_all_kwargs, "100-all_kwargs-True")

    def testMethodBoundToInstance(self) -> None:
        """
        Test ReflectionCallable works with bound methods.

        Validates that ReflectionCallable can properly wrap and introspect
        methods that are bound to class instances, maintaining proper
        method behavior and instance context.

        Raises
        ------
        AssertionError
            If ReflectionCallable fails to handle bound methods correctly
            or loses instance context during introspection.
        """
        class TestClass:
            def test_method(self, value: str) -> str:
                """Test method for bound method testing."""
                return f"method_result_{value}"

        test_instance = TestClass()
        bound_method = test_instance.test_method
        reflection_method = ReflectionCallable(bound_method)

        # Test method properties
        self.assertEqual(reflection_method.getName(), "test_method")
        self.assertTrue(reflection_method.getModuleName().endswith("test_reflection_callable"))

        # Test method execution
        result = reflection_method.call("test_value")
        self.assertEqual(result, "method_result_test_value")

    def testLambdaWithComplexLogic(self) -> None:
        """
        Test ReflectionCallable handles complex lambda expressions.

        Validates that ReflectionCallable can properly wrap and execute
        lambda functions with complex logic, multiple parameters, and
        various return types.

        Raises
        ------
        AssertionError
            If ReflectionCallable fails to handle complex lambda expressions
            or doesn't maintain proper lambda execution semantics.
        """
        def complex_lambda(x, y=10, **kwargs):
            return {
                'sum': x + y,
                'product': x * y,
                'kwargs': kwargs
            }

        reflection_lambda = ReflectionCallable(complex_lambda)

        # Test lambda execution with various parameters
        result = reflection_lambda.call(5, extra="value")
        expected = {'sum': 15, 'product': 50, 'kwargs': {'extra': 'value'}}
        self.assertEqual(result, expected)

        # Test with explicit keyword arguments
        result_kwargs = reflection_lambda.call(3, y=7, additional="data")
        expected_kwargs = {'sum': 10, 'product': 21, 'kwargs': {'additional': 'data'}}
        self.assertEqual(result_kwargs, expected_kwargs)

    def testCallableWithVarArgs(self) -> None:
        """
        Test ReflectionCallable handles functions with variable arguments.

        Validates that ReflectionCallable properly wraps and executes
        functions that accept *args and **kwargs, maintaining proper
        argument unpacking and forwarding behavior.

        Raises
        ------
        AssertionError
            If ReflectionCallable fails to handle variable arguments
            correctly or doesn't maintain proper argument forwarding.
        """
        def varargs_function(*args, **kwargs):
            """Function with variable arguments for testing."""
            return {
                'args_count': len(args),
                'args_values': args,
                'kwargs_count': len(kwargs),
                'kwargs_values': kwargs
            }

        reflection_varargs = ReflectionCallable(varargs_function)

        # Test with multiple positional arguments
        result = reflection_varargs.call(1, 2, 3, name="test", value=42)
        expected = {
            'args_count': 3,
            'args_values': (1, 2, 3),
            'kwargs_count': 2,
            'kwargs_values': {'name': 'test', 'value': 42}
        }
        self.assertEqual(result, expected)

    def testReflectionCallableEquality(self) -> None:
        """
        Test ReflectionCallable instances maintain wrapped callable identity.

        Validates that ReflectionCallable instances properly maintain
        references to their wrapped callables and that multiple instances
        wrapping the same callable are distinguishable.

        Raises
        ------
        AssertionError
            If ReflectionCallable instances don't maintain proper callable
            identity or if wrapped callable references are incorrect.
        """
        # Test same callable wrapped multiple times
        reflection1 = ReflectionCallable(self.sample_function)
        reflection2 = ReflectionCallable(self.sample_function)

        # Both should wrap the same callable
        self.assertEqual(reflection1.getCallable(), reflection2.getCallable())
        self.assertEqual(reflection1.getName(), reflection2.getName())

        # But they should be different ReflectionCallable instances
        self.assertIsNot(reflection1, reflection2)

        # Test different callables
        reflection_different = ReflectionCallable(self.function_with_params)
        self.assertNotEqual(reflection1.getCallable(), reflection_different.getCallable())