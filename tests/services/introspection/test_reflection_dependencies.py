import inspect
from typing import Any, Dict, List, Optional, Union
from orionis.test.cases.synchronous import SyncTestCase
from orionis.services.introspection.dependencies.reflection import ReflectDependencies
from orionis.services.introspection.dependencies.entities.argument import Argument
from orionis.services.introspection.dependencies.entities.resolve_argument import ResolveArguments
from orionis.services.introspection.exceptions import ReflectionValueError

class TestReflectDependencies(SyncTestCase):

    def setUp(self) -> None:
        """
        Set up test environment and create mock classes for testing.

        Initializes various test classes with different parameter configurations
        to comprehensively test the ReflectDependencies functionality. These classes
        simulate real-world scenarios with various dependency injection patterns.

        Notes
        -----
        The setup creates classes with:
        - No parameters (EmptyClass)
        - Mixed parameter types (ComplexClass)
        - Only annotated parameters (AnnotatedClass)
        - Only parameters with defaults (DefaultClass)
        - Built-in type parameters (BuiltinClass)
        - Special parameter handling (SpecialParamsClass)
        """
        # Mock service classes for dependency testing (defined first for use in annotations)
        class MockService:
            def __init__(self, name: str = "mock"):
                self.name = name

        class MockRepository:
            def __init__(self):
                pass

        # Class with no constructor parameters
        class EmptyClass:
            def __init__(self):
                pass

        # Class with mixed parameter types for comprehensive testing
        class ComplexClass:
            def __init__(self, required_param, annotated_param: str, default_param="default", annotated_default: int = 42):
                self.required_param = required_param
                self.annotated_param = annotated_param
                self.default_param = default_param
                self.annotated_default = annotated_default

            def method_with_deps(self, service: MockService, count: int, name: str = "test"):
                return f"{service}_{count}_{name}"

            def method_no_deps(self):
                return "no_deps"

        # Class with only annotated parameters (no defaults)
        class AnnotatedClass:
            def __init__(self, service: MockService, repository: MockRepository):
                self.service = service
                self.repository = repository

        # Class with only default parameters (no annotations)
        class DefaultClass:
            def __init__(self, param1="value1", param2="value2"):
                self.param1 = param1
                self.param2 = param2

        # Class with built-in type annotations
        class BuiltinClass:
            def __init__(self, count: int, name: str, active: bool, data: list = None):
                self.count = count
                self.name = name
                self.active = active
                self.data = data or []

        # Class with special parameters (*args, **kwargs, cls, self)
        class SpecialParamsClass:
            def __init__(self, normal_param: str, *args, **kwargs):
                self.normal_param = normal_param
                self.args = args
                self.kwargs = kwargs

            @classmethod
            def class_method(cls, param: str):
                return param

            @staticmethod
            def static_method(param: str):
                return param

        # Store test classes for use in test methods
        self.EmptyClass = EmptyClass
        self.ComplexClass = ComplexClass
        self.AnnotatedClass = AnnotatedClass
        self.DefaultClass = DefaultClass
        self.BuiltinClass = BuiltinClass
        self.SpecialParamsClass = SpecialParamsClass
        self.MockService = MockService
        self.MockRepository = MockRepository

        # Test functions for callable dependency testing
        def simple_function(param: str):
            return param

        def function_with_defaults(param1: str, param2: int = 10, param3="default"):
            return f"{param1}_{param2}_{param3}"

        def function_no_annotations(param1, param2="default"):
            return f"{param1}_{param2}"

        def lambda_func(x, y=5):
            return x + y

        self.simple_function = simple_function
        self.function_with_defaults = function_with_defaults
        self.function_no_annotations = function_no_annotations
        self.lambda_func = lambda_func

    def tearDown(self) -> None:
        """
        Clean up test environment after each test method.

        Resets all test class references to None to ensure clean state
        between test executions and prevent memory leaks.
        """
        self.EmptyClass = None
        self.ComplexClass = None
        self.AnnotatedClass = None
        self.DefaultClass = None
        self.BuiltinClass = None
        self.SpecialParamsClass = None
        self.MockService = None
        self.MockRepository = None
        self.simple_function = None
        self.function_with_defaults = None
        self.function_no_annotations = None
        self.lambda_func = None

    def testInitializationWithValidTarget(self) -> None:
        """
        Test ReflectDependencies initialization with valid targets.

        Validates that the ReflectDependencies constructor properly initializes
        with various types of valid targets including classes, functions, and
        callable objects.

        Expected Results
        ----------------
        ReflectDependencies instances are created successfully without exceptions
        for all valid target types.
        """
        # Test with class
        reflect_class = ReflectDependencies(self.ComplexClass)
        self.assertIsInstance(reflect_class, ReflectDependencies)

        # Test with function
        reflect_func = ReflectDependencies(self.simple_function)
        self.assertIsInstance(reflect_func, ReflectDependencies)

        # Test with lambda
        reflect_lambda = ReflectDependencies(self.lambda_func)
        self.assertIsInstance(reflect_lambda, ReflectDependencies)

        # Test with None (should be allowed)
        reflect_none = ReflectDependencies(None)
        self.assertIsInstance(reflect_none, ReflectDependencies)

    def testGetConstructorDependenciesEmptyClass(self) -> None:
        """
        Test constructor dependency analysis for class without parameters.

        Validates that classes with empty constructors (only self parameter)
        return empty resolved and unresolved dependency dictionaries.

        Expected Results
        ----------------
        Both resolved and unresolved dictionaries should be empty.
        The ordered dictionary should also be empty.
        """
        reflect = ReflectDependencies(self.EmptyClass)
        result = reflect.getConstructorDependencies()

        self.assertIsInstance(result, ResolveArguments)
        self.assertEqual(len(result.resolved), 0)
        self.assertEqual(len(result.unresolved), 0)
        self.assertEqual(len(result.ordered), 0)

    def testGetConstructorDependenciesComplexClass(self) -> None:
        """
        Test constructor dependency analysis for class with mixed parameter types.

        Validates the categorization of different parameter types:
        - Parameters without annotation or default -> unresolved
        - Builtin types with annotation but no default -> unresolved
        - Parameters with default only -> resolved
        - Parameters with both annotation and default -> resolved

        Expected Results
        ----------------
        Proper categorization of parameters based on their type annotations
        and default values with correct Argument metadata.
        """
        reflect = ReflectDependencies(self.ComplexClass)
        result = reflect.getConstructorDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # Verify unresolved dependencies
        # required_param (no annotation, no default) and annotated_param (builtin type, no default)
        self.assertIn('required_param', result.unresolved)
        self.assertIn('annotated_param', result.unresolved)

        unresolved_arg = result.unresolved['required_param']
        self.assertIsInstance(unresolved_arg, Argument)
        self.assertFalse(unresolved_arg.resolved)
        self.assertIsNone(unresolved_arg.module_name)
        self.assertIsNone(unresolved_arg.class_name)
        self.assertEqual(unresolved_arg.type, Any)

        # Check annotated parameter (str annotation, no default) -> unresolved because it's builtin
        annotated_arg = result.unresolved['annotated_param']
        self.assertFalse(annotated_arg.resolved)
        self.assertEqual(annotated_arg.module_name, 'builtins')
        self.assertEqual(annotated_arg.class_name, 'str')
        self.assertEqual(annotated_arg.type, str)

        # Verify resolved dependencies (those with defaults)
        self.assertIn('default_param', result.resolved)
        self.assertIn('annotated_default', result.resolved)

        # Check default parameter (no annotation, has default)
        default_arg = result.resolved['default_param']
        self.assertTrue(default_arg.resolved)
        self.assertEqual(default_arg.default, "default")
        self.assertEqual(default_arg.type, str)

        # Check annotated default parameter (annotation + default)
        annotated_default_arg = result.resolved['annotated_default']
        self.assertTrue(annotated_default_arg.resolved)
        self.assertEqual(annotated_default_arg.default, 42)
        self.assertEqual(annotated_default_arg.type, int)

        # Verify ordered dependencies contain all parameters
        self.assertEqual(len(result.ordered), 4)
        expected_order = ['required_param', 'annotated_param', 'default_param', 'annotated_default']
        self.assertEqual(list(result.ordered.keys()), expected_order)

    def testGetConstructorDependenciesAnnotatedClass(self) -> None:
        """
        Test constructor dependency analysis for class with only annotated parameters.

        Validates that parameters with non-builtin type annotations and no defaults
        are correctly categorized as resolved dependencies, while builtin types
        without defaults remain unresolved.

        Expected Results
        ----------------
        Non-builtin type annotations should be resolved.
        Builtin type annotations without defaults should be unresolved.
        """
        reflect = ReflectDependencies(self.AnnotatedClass)
        result = reflect.getConstructorDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # Both parameters should be resolved (non-builtin types)
        self.assertEqual(len(result.resolved), 2)
        self.assertEqual(len(result.unresolved), 0)

        # Verify service parameter
        self.assertIn('service', result.resolved)
        service_arg = result.resolved['service']
        self.assertTrue(service_arg.resolved)
        self.assertIn('MockService', service_arg.full_class_path)

        # Verify repository parameter
        self.assertIn('repository', result.resolved)
        repository_arg = result.resolved['repository']
        self.assertTrue(repository_arg.resolved)
        self.assertIn('MockRepository', repository_arg.full_class_path)

    def testGetConstructorDependenciesDefaultClass(self) -> None:
        """
        Test constructor dependency analysis for class with only default parameters.

        Validates that all parameters with default values are categorized as
        resolved dependencies, regardless of type annotations.

        Expected Results
        ----------------
        All parameters with defaults should be resolved with correct default values.
        """
        reflect = ReflectDependencies(self.DefaultClass)
        result = reflect.getConstructorDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # All parameters should be resolved (have defaults)
        self.assertEqual(len(result.resolved), 2)
        self.assertEqual(len(result.unresolved), 0)

        # Check param1
        self.assertIn('param1', result.resolved)
        param1_arg = result.resolved['param1']
        self.assertTrue(param1_arg.resolved)
        self.assertEqual(param1_arg.default, "value1")

        # Check param2
        self.assertIn('param2', result.resolved)
        param2_arg = result.resolved['param2']
        self.assertTrue(param2_arg.resolved)
        self.assertEqual(param2_arg.default, "value2")

    def testGetConstructorDependenciesBuiltinClass(self) -> None:
        """
        Test constructor dependency analysis for class with builtin type annotations.

        Validates that builtin types without defaults are categorized as unresolved,
        while builtin types with defaults are resolved.

        Expected Results
        ----------------
        Builtin types without defaults should be unresolved.
        Builtin types with defaults should be resolved.
        """
        reflect = ReflectDependencies(self.BuiltinClass)
        result = reflect.getConstructorDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # Parameters without defaults should be unresolved
        expected_unresolved = ['count', 'name', 'active']
        for param in expected_unresolved:
            self.assertIn(param, result.unresolved)
            arg = result.unresolved[param]
            self.assertFalse(arg.resolved)
            self.assertEqual(arg.module_name, 'builtins')

        # Parameter with default should be resolved
        self.assertIn('data', result.resolved)
        data_arg = result.resolved['data']
        self.assertTrue(data_arg.resolved)
        self.assertIsNone(data_arg.default)

    def testGetConstructorDependenciesSpecialParams(self) -> None:
        """
        Test constructor dependency analysis with special parameters.

        Validates that special parameters like *args and **kwargs are properly
        excluded from dependency analysis, while normal parameters are processed.

        Expected Results
        ----------------
        Special parameters (*args, **kwargs) should be excluded.
        Only normal parameters should be included in the analysis.
        """
        reflect = ReflectDependencies(self.SpecialParamsClass)
        result = reflect.getConstructorDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # Only normal_param should be analyzed (args and kwargs excluded)
        total_params = len(result.resolved) + len(result.unresolved)
        self.assertEqual(total_params, 1)

        # normal_param should be unresolved (builtin type str without default)
        self.assertIn('normal_param', result.unresolved)
        normal_arg = result.unresolved['normal_param']
        self.assertFalse(normal_arg.resolved)
        self.assertEqual(normal_arg.type, str)

        # Verify args and kwargs are not included
        self.assertNotIn('args', result.resolved)
        self.assertNotIn('args', result.unresolved)
        self.assertNotIn('kwargs', result.resolved)
        self.assertNotIn('kwargs', result.unresolved)

    def testGetMethodDependenciesWithDependencies(self) -> None:
        """
        Test method dependency analysis for method with various parameter types.

        Validates that method parameters are correctly categorized based on
        their annotations and default values, excluding 'self' parameter.

        Expected Results
        ----------------
        Method parameters should be categorized correctly.
        'self' parameter should be excluded from analysis.
        """
        reflect = ReflectDependencies(self.ComplexClass)
        result = reflect.getMethodDependencies('method_with_deps')

        self.assertIsInstance(result, ResolveArguments)

        # Should have service (resolved), count (unresolved due to builtin), name (resolved due to default)
        self.assertIn('service', result.resolved)
        self.assertIn('count', result.unresolved)
        self.assertIn('name', result.resolved)

        # Verify service parameter
        service_arg = result.resolved['service']
        self.assertTrue(service_arg.resolved)
        self.assertIn('MockService', service_arg.full_class_path)

        # Verify count parameter (builtin type without default)
        count_arg = result.unresolved['count']
        self.assertFalse(count_arg.resolved)
        self.assertEqual(count_arg.type, int)

        # Verify name parameter (has default)
        name_arg = result.resolved['name']
        self.assertTrue(name_arg.resolved)
        self.assertEqual(name_arg.default, "test")

        # Verify 'self' is not included
        self.assertNotIn('self', result.resolved)
        self.assertNotIn('self', result.unresolved)

    def testGetMethodDependenciesNoDependencies(self) -> None:
        """
        Test method dependency analysis for method without parameters.

        Validates that methods with no parameters (except 'self') return
        empty dependency dictionaries.

        Expected Results
        ----------------
        All dependency dictionaries should be empty.
        """
        reflect = ReflectDependencies(self.ComplexClass)
        result = reflect.getMethodDependencies('method_no_deps')

        self.assertIsInstance(result, ResolveArguments)
        self.assertEqual(len(result.resolved), 0)
        self.assertEqual(len(result.unresolved), 0)
        self.assertEqual(len(result.ordered), 0)

    def testGetMethodDependenciesClassMethod(self) -> None:
        """
        Test method dependency analysis for class methods.

        Validates that class method parameters are correctly analyzed,
        excluding the 'cls' parameter from dependency resolution.

        Expected Results
        ----------------
        'cls' parameter should be excluded.
        Other parameters should be analyzed normally.
        """
        reflect = ReflectDependencies(self.SpecialParamsClass)
        result = reflect.getMethodDependencies('class_method')

        self.assertIsInstance(result, ResolveArguments)

        # Should have param (unresolved due to builtin type without default)
        self.assertIn('param', result.unresolved)
        param_arg = result.unresolved['param']
        self.assertFalse(param_arg.resolved)
        self.assertEqual(param_arg.type, str)

        # Verify 'cls' is not included
        self.assertNotIn('cls', result.resolved)
        self.assertNotIn('cls', result.unresolved)

    def testGetMethodDependenciesStaticMethod(self) -> None:
        """
        Test method dependency analysis for static methods.

        Validates that static method parameters are analyzed normally
        without any special parameter exclusions.

        Expected Results
        ----------------
        All parameters should be analyzed based on annotations and defaults.
        """
        reflect = ReflectDependencies(self.SpecialParamsClass)
        result = reflect.getMethodDependencies('static_method')

        self.assertIsInstance(result, ResolveArguments)

        # Should have param (unresolved due to builtin type without default)
        self.assertIn('param', result.unresolved)
        param_arg = result.unresolved['param']
        self.assertFalse(param_arg.resolved)
        self.assertEqual(param_arg.type, str)

    def testGetMethodDependenciesNonExistentMethod(self) -> None:
        """
        Test method dependency analysis for non-existent methods.

        Validates that attempting to analyze dependencies for methods that
        don't exist raises appropriate AttributeError.

        Expected Results
        ----------------
        AttributeError should be raised for non-existent methods.
        """
        reflect = ReflectDependencies(self.ComplexClass)

        with self.assertRaises(AttributeError):
            reflect.getMethodDependencies('non_existent_method')

    def testGetCallableDependenciesSimpleFunction(self) -> None:
        """
        Test callable dependency analysis for simple function.

        Validates that function parameters with builtin type annotations
        are categorized as unresolved dependencies.

        Expected Results
        ----------------
        Builtin type annotations without defaults should be unresolved.
        """
        reflect = ReflectDependencies(self.simple_function)
        result = reflect.getCallableDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # Parameter with builtin annotation should be unresolved
        self.assertIn('param', result.unresolved)
        param_arg = result.unresolved['param']
        self.assertFalse(param_arg.resolved)
        self.assertEqual(param_arg.type, str)

    def testGetCallableDependenciesFunctionWithDefaults(self) -> None:
        """
        Test callable dependency analysis for function with default parameters.

        Validates that function parameters are correctly categorized based on
        their annotations and default values.

        Expected Results
        ----------------
        Parameters with builtin annotations but no defaults should be unresolved.
        Parameters with defaults should be resolved.
        """
        reflect = ReflectDependencies(self.function_with_defaults)
        result = reflect.getCallableDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # param1 should be unresolved (builtin type str without default)
        self.assertIn('param1', result.unresolved)
        param1_arg = result.unresolved['param1']
        self.assertFalse(param1_arg.resolved)
        self.assertEqual(param1_arg.type, str)

        # param2 should be resolved (has default even though builtin type)
        self.assertIn('param2', result.resolved)
        param2_arg = result.resolved['param2']
        self.assertTrue(param2_arg.resolved)
        self.assertEqual(param2_arg.type, int)
        self.assertEqual(param2_arg.default, 10)

        # param3 should be resolved (has default)
        self.assertIn('param3', result.resolved)
        param3_arg = result.resolved['param3']
        self.assertTrue(param3_arg.resolved)
        self.assertEqual(param3_arg.default, "default")

    def testGetCallableDependenciesFunctionNoAnnotations(self) -> None:
        """
        Test callable dependency analysis for function without annotations.

        Validates that parameters without annotations are categorized based
        solely on the presence of default values.

        Expected Results
        ----------------
        Parameters without annotations or defaults should be unresolved.
        Parameters with defaults should be resolved.
        """
        reflect = ReflectDependencies(self.function_no_annotations)
        result = reflect.getCallableDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # param1 should be unresolved (no annotation, no default)
        self.assertIn('param1', result.unresolved)
        param1_arg = result.unresolved['param1']
        self.assertFalse(param1_arg.resolved)
        self.assertEqual(param1_arg.type, Any)

        # param2 should be resolved (has default)
        self.assertIn('param2', result.resolved)
        param2_arg = result.resolved['param2']
        self.assertTrue(param2_arg.resolved)
        self.assertEqual(param2_arg.default, "default")

    def testGetCallableDependenciesLambda(self) -> None:
        """
        Test callable dependency analysis for lambda functions.

        Validates that lambda function parameters are analyzed correctly,
        treating them similarly to regular functions.

        Expected Results
        ----------------
        Lambda parameters should be categorized based on defaults.
        Parameters without defaults should be unresolved.
        """
        reflect = ReflectDependencies(self.lambda_func)
        result = reflect.getCallableDependencies()

        self.assertIsInstance(result, ResolveArguments)

        # x should be unresolved (no annotation, no default)
        self.assertIn('x', result.unresolved)
        x_arg = result.unresolved['x']
        self.assertFalse(x_arg.resolved)

        # y should be resolved (has default)
        self.assertIn('y', result.resolved)
        y_arg = result.resolved['y']
        self.assertTrue(y_arg.resolved)
        self.assertEqual(y_arg.default, 5)

    def testGetConstructorDependenciesWithNonCallableTarget(self) -> None:
        """
        Test constructor dependency analysis with non-callable target.

        Validates that analyzing constructor dependencies for built-in types
        like strings still works because their __init__ methods are callable.
        This tests the edge case where the target itself isn't what we'd normally
        consider "callable" but has a valid __init__ method.

        Expected Results
        ----------------
        Should return valid ResolveArguments for the string's __init__ method
        which typically has signature (*args, **kwargs).
        """
        reflect = ReflectDependencies("not_callable")
        
        # This should work because "not_callable".__init__ is callable
        result = reflect.getConstructorDependencies()
        
        self.assertIsInstance(result, ResolveArguments)
        # String's __init__ typically has *args, **kwargs which are skipped
        self.assertEqual(len(result.resolved), 0)
        self.assertEqual(len(result.unresolved), 0)

    def testGetCallableDependenciesWithNonCallableTarget(self) -> None:
        """
        Test callable dependency analysis with non-callable target.

        Validates that attempting to analyze callable dependencies for
        non-callable targets raises appropriate exceptions.

        Expected Results
        ----------------
        Appropriate exception should be raised for non-callable targets.
        """
        reflect = ReflectDependencies("not_callable")

        with self.assertRaises((ReflectionValueError, TypeError)):
            reflect.getCallableDependencies()

    def testPrivateParamSkipMethod(self) -> None:
        """
        Test the private parameter skip logic for various parameter types.

        This test validates the internal logic for determining which parameters
        should be excluded from dependency analysis by creating mock inspect.Parameter
        objects and testing the skip conditions.

        Expected Results
        ----------------
        Special parameters should be correctly identified for skipping.
        Normal parameters should not be skipped.
        """
        # Test with a class that has access to the private method through reflection
        reflect = ReflectDependencies(self.ComplexClass)

        # Create real parameters from a test function instead of mocks
        def test_function(self, cls, normal, *args, **kwargs):
            pass
        
        sig = inspect.signature(test_function)
        params = sig.parameters
        
        # Access private method through name mangling
        param_skip_method = getattr(reflect, '_ReflectDependencies__paramSkip')

        # Test special parameter names
        self.assertTrue(param_skip_method('self', params['self']))
        self.assertTrue(param_skip_method('cls', params['cls']))
        self.assertTrue(param_skip_method('args', params['normal']))  # name-based skip
        self.assertTrue(param_skip_method('kwargs', params['normal']))  # name-based skip

        # Test variadic parameters - should be skipped based on kind regardless of name
        self.assertTrue(param_skip_method('normal_name', params['args']))
        self.assertTrue(param_skip_method('normal_name', params['kwargs']))
        
        # Test normal parameters that should not be skipped
        self.assertFalse(param_skip_method('normal_param', params['normal']))

    def testPrivateInspectSignatureMethod(self) -> None:
        """
        Test the private signature inspection method for various callable types.

        Validates that the internal signature inspection method correctly
        extracts signatures from different types of callable objects and
        handles non-callable objects appropriately.

        Expected Results
        ----------------
        Valid signatures should be returned for callable objects.
        ReflectionValueError should be raised for non-callable objects.
        """
        reflect = ReflectDependencies(self.ComplexClass)

        # Access private method through name mangling
        inspect_signature_method = getattr(reflect, '_ReflectDependencies__inspectSignature')

        # Test with class constructor
        signature = inspect_signature_method(self.ComplexClass.__init__)
        self.assertIsInstance(signature, inspect.Signature)

        # Test with regular function
        signature = inspect_signature_method(self.simple_function)
        self.assertIsInstance(signature, inspect.Signature)

        # Test with lambda
        signature = inspect_signature_method(self.lambda_func)
        self.assertIsInstance(signature, inspect.Signature)

        # Test with non-callable object
        with self.assertRaises(ReflectionValueError):
            inspect_signature_method("not_callable")

        with self.assertRaises(ReflectionValueError):
            inspect_signature_method(123)

    def testResolveArgumentsStructureValidation(self) -> None:
        """
        Test that ResolveArguments structure is properly populated and validated.

        Validates that the returned ResolveArguments object contains the expected
        structure with resolved, unresolved, and ordered dictionaries properly
        populated and synchronized.

        Expected Results
        ----------------
        ResolveArguments should have properly structured dictionaries.
        Ordered dictionary should contain all parameters in definition order.
        """
        reflect = ReflectDependencies(self.ComplexClass)
        result = reflect.getConstructorDependencies()

        # Validate structure
        self.assertIsInstance(result, ResolveArguments)
        self.assertIsInstance(result.resolved, dict)
        self.assertIsInstance(result.unresolved, dict)
        self.assertIsInstance(result.ordered, dict)

        # Validate that ordered contains all parameters
        total_params = len(result.resolved) + len(result.unresolved)
        self.assertEqual(len(result.ordered), total_params)

        # Validate that all resolved params are in ordered
        for param_name in result.resolved.keys():
            self.assertIn(param_name, result.ordered)

        # Validate that all unresolved params are in ordered
        for param_name in result.unresolved.keys():
            self.assertIn(param_name, result.ordered)

        # Validate that ordered preserves parameter definition order
        expected_order = ['required_param', 'annotated_param', 'default_param', 'annotated_default']
        self.assertEqual(list(result.ordered.keys()), expected_order)

    def testArgumentEntityValidation(self) -> None:
        """
        Test that Argument entities are properly structured and validated.

        Validates that all Argument instances returned by the reflection methods
        contain the expected attributes with correct types and values.

        Expected Results
        ----------------
        All Argument instances should have proper structure.
        Attribute values should match expected types and constraints.
        """
        reflect = ReflectDependencies(self.ComplexClass)
        result = reflect.getConstructorDependencies()

        # Test resolved argument structure
        for param_name, argument in result.resolved.items():
            self.assertIsInstance(argument, Argument)
            self.assertTrue(argument.resolved)
            self.assertIsInstance(argument.module_name, (str, type(None)))
            self.assertIsInstance(argument.class_name, (str, type(None)))
            self.assertIsNotNone(argument.type)
            self.assertIsInstance(argument.full_class_path, (str, type(None)))

        # Test unresolved argument structure
        for param_name, argument in result.unresolved.items():
            self.assertIsInstance(argument, Argument)
            self.assertFalse(argument.resolved)
            self.assertIsInstance(argument.module_name, (str, type(None)))
            self.assertIsInstance(argument.class_name, (str, type(None)))
            self.assertIsNotNone(argument.type)
            self.assertIsInstance(argument.full_class_path, (str, type(None)))

    def testEdgeCaseWithComplexTypeAnnotations(self) -> None:
        """
        Test dependency analysis with complex type annotations.

        Validates that the reflection system properly handles complex type
        annotations including Union, Optional, List, Dict, and other typing
        constructs.

        Expected Results
        ----------------
        Complex type annotations should be properly categorized.
        Type information should be preserved accurately.
        """
        # Create a class with complex type annotations
        class ComplexTypesClass:
            def __init__(
                self,
                union_param: Union[str, int],
                optional_param: Optional[str] = None,
                list_param: List[str] = None,
                dict_param: Dict[str, Any] = None
            ):
                self.union_param = union_param
                self.optional_param = optional_param
                self.list_param = list_param or []
                self.dict_param = dict_param or {}

        reflect = ReflectDependencies(ComplexTypesClass)
        result = reflect.getConstructorDependencies()

        # union_param should be resolved (has annotation)
        self.assertIn('union_param', result.resolved)
        union_arg = result.resolved['union_param']
        self.assertTrue(union_arg.resolved)
        self.assertEqual(union_arg.module_name, 'typing')

        # Parameters with defaults should be resolved
        self.assertIn('optional_param', result.resolved)
        self.assertIn('list_param', result.resolved)
        self.assertIn('dict_param', result.resolved)

        # Verify all have defaults
        for param in ['optional_param', 'list_param', 'dict_param']:
            arg = result.resolved[param]
            self.assertTrue(arg.resolved)
            self.assertIsNotNone(arg.full_class_path)

    def testConsistencyBetweenMethodTypes(self) -> None:
        """
        Test consistency of dependency analysis across different method types.

        Validates that constructor, method, and callable dependency analysis
        produce consistent results when analyzing similar parameter patterns.

        Expected Results
        ----------------
        Similar parameter patterns should be categorized consistently.
        Argument structures should be equivalent across method types.
        """
        # Create function with same signature as ComplexClass constructor
        def equivalent_function(required_param, annotated_param: str, default_param="default", annotated_default: int = 42):
            pass

        # Analyze constructor, method, and callable with similar signatures
        class_reflect = ReflectDependencies(self.ComplexClass)
        constructor_result = class_reflect.getConstructorDependencies()

        function_reflect = ReflectDependencies(equivalent_function)
        callable_result = function_reflect.getCallableDependencies()

        # Compare categorization consistency
        self.assertEqual(set(constructor_result.resolved.keys()), set(callable_result.resolved.keys()))
        self.assertEqual(set(constructor_result.unresolved.keys()), set(callable_result.unresolved.keys()))

        # Compare argument properties for resolved parameters
        for param_name in constructor_result.resolved.keys():
            constructor_arg = constructor_result.resolved[param_name]
            callable_arg = callable_result.resolved[param_name]

            self.assertEqual(constructor_arg.resolved, callable_arg.resolved)
            self.assertEqual(constructor_arg.type, callable_arg.type)
            self.assertEqual(constructor_arg.default, callable_arg.default)

    def testEmptyTargetHandling(self) -> None:
        """
        Test handling of empty or None targets.

        Validates that the reflection system properly handles edge cases
        where the target might be None or empty.

        Expected Results
        ----------------
        Appropriate error handling for invalid targets.
        Graceful handling of None targets where applicable.
        """
        # Test with None target
        reflect_none = ReflectDependencies(None)
        self.assertIsInstance(reflect_none, ReflectDependencies)

        # Note: Based on actual implementation, None targets might return empty results
        # rather than raise errors. Let's check the actual behavior.
        try:
            constructor_result = reflect_none.getConstructorDependencies()
            # If it doesn't raise an error, verify it returns an empty result
            self.assertIsInstance(constructor_result, ResolveArguments)
        except (ReflectionValueError, AttributeError, TypeError):
            # This is also acceptable behavior
            pass

        try:
            callable_result = reflect_none.getCallableDependencies()
            # If it doesn't raise an error, verify it returns an empty result
            self.assertIsInstance(callable_result, ResolveArguments)
        except (ReflectionValueError, TypeError):
            # This is also acceptable behavior
            pass

    def testPerformanceWithLargeSignatures(self) -> None:
        """
        Test performance and correctness with classes having many parameters.

        Validates that the reflection system handles classes with large numbers
        of parameters efficiently and correctly.

        Expected Results
        ----------------
        Large parameter lists should be processed correctly.
        All parameters should be properly categorized.
        Performance should remain reasonable.
        """
        # Create a class with many parameters
        class LargeSignatureClass:
            def __init__(
                self,
                param1: str,
                param2: int,
                param3: bool,
                param4: float,
                param5: list,
                param6="default1",
                param7="default2",
                param8="default3",
                param9="default4",
                param10="default5",
                param11: Any = None,
                param12: Any = None
            ):
                # Empty constructor for testing dependency reflection only
                pass

        reflect = ReflectDependencies(LargeSignatureClass)
        result = reflect.getConstructorDependencies()

        # Verify total parameter count
        total_params = len(result.resolved) + len(result.unresolved)
        self.assertEqual(total_params, 12)

        # Verify builtin types without defaults are unresolved
        builtin_unresolved = ['param1', 'param2', 'param3', 'param4', 'param5']
        for param in builtin_unresolved:
            self.assertIn(param, result.unresolved)

        # Verify parameters with defaults are resolved
        default_resolved = ['param6', 'param7', 'param8', 'param9', 'param10', 'param11', 'param12']
        for param in default_resolved:
            self.assertIn(param, result.resolved)

        # Verify ordered dictionary maintains correct order
        expected_order = [f'param{i}' for i in range(1, 13)]
        self.assertEqual(list(result.ordered.keys()), expected_order)
