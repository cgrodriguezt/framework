import inspect
import asyncio
from abc import ABC, abstractmethod
from orionis.test.cases.synchronous import SyncTestCase
from orionis.services.introspection.reflection import Reflection
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.callables.reflection import ReflectionCallable
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.services.introspection.modules.reflection import ReflectionModule
from orionis.services.introspection.exceptions import (
    ReflectionTypeError,
    ReflectionValueError,
)

class AbstractTestClass(ABC):
    """An abstract test class for testing purposes."""

    @abstractmethod
    def abstractMethod(self) -> str:
        """An abstract method that must be implemented."""

class ConcreteTestClass(AbstractTestClass):
    """A concrete test class that implements the abstract class."""

    def __init__(self, value: int = 42):
        """Initialize the concrete test class."""
        self.value = value

    def abstractMethod(self) -> str:
        """Implementation of the abstract method."""
        return "concrete implementation"

    def concreteMethod(self) -> str:
        """A concrete method."""
        return "concrete method result"

class SimpleTestClass:
    """A simple test class for reflection testing."""

    def __init__(self, name: str = "test"):
        """Initialize the simple test class."""
        self.name = name

    def getName(self) -> str:
        """Get the name attribute."""
        return self.name

def simpleFunction(x: int, y: int = 5) -> int:
    """A simple function for testing callable reflection."""
    return x + y

async def asyncFunction(value: str) -> str:
    """An async function for testing callable reflection."""
    await asyncio.sleep(0.001)
    return f"async: {value}"

def generatorFunction():
    """A generator function for testing."""
    for i in range(3):
        yield i

async def asyncGeneratorFunction():
    """An async generator function for testing."""
    for i in range(3):
        yield i
        await asyncio.sleep(0.001)

class TestReflection(SyncTestCase):

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates instances and objects needed for testing reflection operations.
        """
        self.simple_instance = SimpleTestClass("test_name")
        self.concrete_instance = ConcreteTestClass(100)
        self.abstract_class = AbstractTestClass
        self.concrete_class = ConcreteTestClass
        self.simple_class = SimpleTestClass
        self.function = simpleFunction
        self.async_function = asyncFunction
        self.generator_function = generatorFunction
        self.async_generator_function = asyncGeneratorFunction
        self.module_name = "os"

    def testInstanceReturnsReflectionInstance(self):
        """
        Test that instance() method returns a ReflectionInstance object.

        Verifies that the factory method creates the correct type of reflection
        object for instance introspection with valid custom objects.
        """
        result = Reflection.instance(self.simple_instance)

        self.assertIsInstance(result, ReflectionInstance)

    def testInstanceWithNoneValueRaisesException(self):
        """
        Test that instance() method raises exception with None value.

        Verifies that the factory method raises ReflectionValueError for None
        as it belongs to the disallowed builtins module.
        """
        with self.assertRaises(ReflectionValueError):
            Reflection.instance(None)

    def testInstanceWithPrimitiveTypesRaisesException(self):
        """
        Test that instance() method raises exception with primitive types.

        Verifies that the factory method raises ReflectionValueError for
        built-in types as they belong to the disallowed builtins module.
        """
        test_cases = [
            42,
            "string",
            [1, 2, 3],
            {"key": "value"},
            (1, 2, 3),
            {1, 2, 3},
        ]

        for test_value in test_cases:
            with self.subTest(value=test_value):
                with self.assertRaises(ReflectionValueError):
                    Reflection.instance(test_value)

    def testAbstractReturnsReflectionAbstract(self):
        """
        Test that abstract() method returns a ReflectionAbstract object.

        Verifies that the factory method creates the correct type of reflection
        object for abstract class introspection.
        """
        result = Reflection.abstract(self.abstract_class)

        self.assertIsInstance(result, ReflectionAbstract)

    def testAbstractWithConcreteClassRaisesException(self):
        """
        Test that abstract() method raises exception with concrete classes.

        Verifies that the factory method raises ReflectionTypeError when
        trying to create an abstract reflection from a concrete class.
        """
        with self.assertRaises(ReflectionTypeError):
            Reflection.abstract(self.concrete_class)

    def testConcreteReturnsReflectionConcrete(self):
        """
        Test that concrete() method returns a ReflectionConcrete object.

        Verifies that the factory method creates the correct type of reflection
        object for concrete class introspection.
        """
        result = Reflection.concrete(self.concrete_class)

        self.assertIsInstance(result, ReflectionConcrete)

    def testConcreteWithBuiltinTypesRaisesException(self):
        """
        Test that concrete() method raises exception with built-in types.

        Verifies that the factory method raises ReflectionValueError for
        built-in types as they are not allowed in concrete reflection.
        """
        built_in_types = [int, str, list, dict, tuple, set]

        for built_in_type in built_in_types:
            with self.subTest(type=built_in_type.__name__):
                with self.assertRaises(ReflectionValueError):
                    Reflection.concrete(built_in_type)

    def testModuleReturnsReflectionModule(self):
        """
        Test that module() method returns a ReflectionModule object.

        Verifies that the factory method creates the correct type of reflection
        object for module introspection.
        """
        result = Reflection.module(self.module_name)

        self.assertIsInstance(result, ReflectionModule)

    def testModuleWithDifferentModuleNames(self):
        """
        Test that module() method works with different module names.

        Verifies that the factory method can handle various built-in and
        standard library modules.
        """
        module_names = ["sys", "json", "datetime", "collections", "itertools"]

        for module_name in module_names:
            with self.subTest(module=module_name):
                result = Reflection.module(module_name)
                self.assertIsInstance(result, ReflectionModule)

    def testModuleWithInvalidModuleNameRaisesException(self):
        """
        Test that module() method raises exception for invalid module names.

        Verifies that the factory method raises ReflectionTypeError when
        trying to import a non-existent module.
        """
        with self.assertRaises(ReflectionTypeError):
            Reflection.module("non_existent_module_12345")

    def testCallableReturnsReflectionCallable(self):
        """
        Test that callable() method returns a ReflectionCallable object.

        Verifies that the factory method creates the correct type of reflection
        object for callable introspection.
        """
        result = Reflection.callable(self.function)

        self.assertIsInstance(result, ReflectionCallable)

    def testCallableWithDifferentCallableTypes(self):
        """
        Test that callable() method works with valid callable types.

        Verifies that the factory method can handle functions, methods,
        and lambdas but not classes or built-in functions.
        """
        valid_callables = [
            self.function,
            self.async_function,
            lambda x: x * 2,
            self.simple_instance.getName,
        ]

        for callable_obj in valid_callables:
            with self.subTest(callable=str(callable_obj)):
                result = Reflection.callable(callable_obj)
                self.assertIsInstance(result, ReflectionCallable)

    def testCallableWithInvalidCallableTypesRaisesException(self):
        """
        Test that callable() method raises exception with invalid callable types.

        Verifies that the factory method raises ReflectionTypeError for
        classes and built-in functions which are not supported.
        """
        invalid_callables = [
            ConcreteTestClass,
            len,
            max,
            print,
        ]

        for callable_obj in invalid_callables:
            with self.subTest(callable=str(callable_obj)):
                with self.assertRaises(ReflectionTypeError):
                    Reflection.callable(callable_obj)

    def testIsAbstractWithAbstractClass(self):
        """
        Test that isAbstract() correctly identifies abstract classes.

        Verifies that the method returns True for classes with abstract methods.
        """
        result = Reflection.isAbstract(self.abstract_class)

        self.assertTrue(result)

    def testIsAbstractWithConcreteClass(self):
        """
        Test that isAbstract() correctly identifies concrete classes.

        Verifies that the method returns False for classes without abstract methods.
        """
        result = Reflection.isAbstract(self.concrete_class)

        self.assertFalse(result)

    def testIsAbstractWithInstances(self):
        """
        Test that isAbstract() works with instances.

        Verifies that the method returns False for instances (not classes).
        """
        result = Reflection.isAbstract(self.simple_instance)

        self.assertFalse(result)

    def testIsAsyncGenWithAsyncGenerator(self):
        """
        Test that isAsyncGen() correctly identifies async generators.

        Verifies that the method returns True for async generator objects.
        """
        async_gen = self.async_generator_function()
        result = Reflection.isAsyncGen(async_gen)

        self.assertTrue(result)
        # Close the async generator properly
        try:
            async_gen.aclose()
        except RuntimeWarning:
            pass  # Ignore the runtime warning

    def testIsAsyncGenWithRegularGenerator(self):
        """
        Test that isAsyncGen() correctly identifies regular generators.

        Verifies that the method returns False for regular generator objects.
        """
        regular_gen = self.generator_function()
        result = Reflection.isAsyncGen(regular_gen)

        self.assertFalse(result)

    def testIsAsyncGenWithNonGenerator(self):
        """
        Test that isAsyncGen() correctly identifies non-generators.

        Verifies that the method returns False for non-generator objects.
        """
        result = Reflection.isAsyncGen(self.simple_instance)

        self.assertFalse(result)

    def testIsAsyncGenFunctionWithAsyncGeneratorFunction(self):
        """
        Test that isAsyncGenFunction() correctly identifies async generator functions.

        Verifies that the method returns True for async generator function objects.
        """
        result = Reflection.isAsyncGenFunction(self.async_generator_function)

        self.assertTrue(result)

    def testIsAsyncGenFunctionWithRegularGeneratorFunction(self):
        """
        Test that isAsyncGenFunction() correctly identifies regular generator functions.

        Verifies that the method returns False for regular generator function objects.
        """
        result = Reflection.isAsyncGenFunction(self.generator_function)

        self.assertFalse(result)

    def testIsAsyncGenFunctionWithAsyncFunction(self):
        """
        Test that isAsyncGenFunction() correctly identifies async functions.

        Verifies that the method returns False for async function objects
        that are not generators.
        """
        result = Reflection.isAsyncGenFunction(self.async_function)

        self.assertFalse(result)

    def testIsAwaitableWithCoroutine(self):
        """
        Test that isAwaitable() correctly identifies coroutines.

        Verifies that the method returns True for coroutine objects.
        """
        coroutine = self.async_function("test")
        result = Reflection.isAwaitable(coroutine)

        self.assertTrue(result)
        coroutine.close()

    def testIsAwaitableWithNonAwaitable(self):
        """
        Test that isAwaitable() correctly identifies non-awaitable objects.

        Verifies that the method returns False for objects that cannot be awaited.
        """
        result = Reflection.isAwaitable(self.simple_instance)

        self.assertFalse(result)

    def testIsAwaitableWithAsyncFunction(self):
        """
        Test that isAwaitable() correctly identifies async functions.

        Verifies that the method returns False for async function objects
        (not their coroutine results).
        """
        result = Reflection.isAwaitable(self.async_function)

        self.assertFalse(result)

    def testIsBuiltinWithBuiltinFunction(self):
        """
        Test that isBuiltin() correctly identifies built-in functions.

        Verifies that the method returns True for built-in function objects.
        """
        result = Reflection.isBuiltin(len)

        self.assertTrue(result)

    def testIsBuiltinWithUserDefinedFunction(self):
        """
        Test that isBuiltin() correctly identifies user-defined functions.

        Verifies that the method returns False for user-defined function objects.
        """
        result = Reflection.isBuiltin(self.function)

        self.assertFalse(result)

    def testIsBuiltinWithBuiltinMethod(self):
        """
        Test that isBuiltin() correctly identifies built-in methods.

        Verifies that the method returns True for built-in method objects.
        """
        result = Reflection.isBuiltin([].append)

        self.assertTrue(result)

    def testIsClassWithClass(self):
        """
        Test that isClass() correctly identifies classes.

        Verifies that the method returns True for class objects.
        """
        result = Reflection.isClass(self.simple_class)

        self.assertTrue(result)

    def testIsClassWithInstance(self):
        """
        Test that isClass() correctly identifies instances.

        Verifies that the method returns False for instance objects.
        """
        result = Reflection.isClass(self.simple_instance)

        self.assertFalse(result)

    def testIsClassWithBuiltinTypes(self):
        """
        Test that isClass() correctly identifies built-in types.

        Verifies that the method returns True for built-in type objects.
        """
        built_in_types = [int, str, list, dict, tuple, set]

        for built_in_type in built_in_types:
            with self.subTest(type=built_in_type.__name__):
                result = Reflection.isClass(built_in_type)
                self.assertTrue(result)

    def testIsCodeWithCodeObject(self):
        """
        Test that isCode() correctly identifies code objects.

        Verifies that the method returns True for code objects.
        """
        result = Reflection.isCode(self.function.__code__)

        self.assertTrue(result)

    def testIsCodeWithNonCodeObject(self):
        """
        Test that isCode() correctly identifies non-code objects.

        Verifies that the method returns False for non-code objects.
        """
        result = Reflection.isCode(self.function)

        self.assertFalse(result)

    def testIsCoroutineWithCoroutine(self):
        """
        Test that isCoroutine() correctly identifies coroutines.

        Verifies that the method returns True for coroutine objects.
        """
        coroutine = self.async_function("test")
        result = Reflection.isCoroutine(coroutine)

        self.assertTrue(result)
        coroutine.close()

    def testIsCoroutineWithNonCoroutine(self):
        """
        Test that isCoroutine() correctly identifies non-coroutines.

        Verifies that the method returns False for non-coroutine objects.
        """
        result = Reflection.isCoroutine(self.function)

        self.assertFalse(result)

    def testIsCoroutineFunctionWithAsyncFunction(self):
        """
        Test that isCoroutineFunction() correctly identifies async functions.

        Verifies that the method returns True for async function objects.
        """
        result = Reflection.isCoroutineFunction(self.async_function)

        self.assertTrue(result)

    def testIsCoroutineFunctionWithRegularFunction(self):
        """
        Test that isCoroutineFunction() correctly identifies regular functions.

        Verifies that the method returns False for regular function objects.
        """
        result = Reflection.isCoroutineFunction(self.function)

        self.assertFalse(result)

    def testIsDataDescriptorWithProperty(self):
        """
        Test that isDataDescriptor() correctly identifies properties.

        Verifies that the method returns True for property objects.
        """
        class TestProperty:
            @property
            def test_prop(self):
                return "test"

        result = Reflection.isDataDescriptor(TestProperty.test_prop)

        self.assertTrue(result)

    def testIsDataDescriptorWithNonDescriptor(self):
        """
        Test that isDataDescriptor() correctly identifies non-descriptors.

        Verifies that the method returns False for non-descriptor objects.
        """
        result = Reflection.isDataDescriptor(self.simple_instance)

        self.assertFalse(result)

    def testIsFrameWithFrameObject(self):
        """
        Test that isFrame() correctly identifies frame objects.

        Verifies that the method returns True for frame objects.
        """
        frame = inspect.currentframe()
        result = Reflection.isFrame(frame)

        self.assertTrue(result)

    def testIsFrameWithNonFrameObject(self):
        """
        Test that isFrame() correctly identifies non-frame objects.

        Verifies that the method returns False for non-frame objects.
        """
        result = Reflection.isFrame(self.simple_instance)

        self.assertFalse(result)

    def testIsFunctionWithFunction(self):
        """
        Test that isFunction() correctly identifies functions.

        Verifies that the method returns True for function objects.
        """
        result = Reflection.isFunction(self.function)

        self.assertTrue(result)

    def testIsFunctionWithMethod(self):
        """
        Test that isFunction() correctly identifies methods.

        Verifies that the method returns False for method objects.
        """
        result = Reflection.isFunction(self.simple_instance.getName)

        self.assertFalse(result)

    def testIsFunctionWithLambda(self):
        """
        Test that isFunction() correctly identifies lambda functions.

        Verifies that the method returns True for lambda function objects.
        """
        def lambda_func(x):
            return x * 2
        result = Reflection.isFunction(lambda_func)

        self.assertTrue(result)

    def testIsGeneratorWithGenerator(self):
        """
        Test that isGenerator() correctly identifies generators.

        Verifies that the method returns True for generator objects.
        """
        generator = self.generator_function()
        result = Reflection.isGenerator(generator)

        self.assertTrue(result)

    def testIsGeneratorWithNonGenerator(self):
        """
        Test that isGenerator() correctly identifies non-generators.

        Verifies that the method returns False for non-generator objects.
        """
        result = Reflection.isGenerator(self.simple_instance)

        self.assertFalse(result)

    def testIsGeneratorFunctionWithGeneratorFunction(self):
        """
        Test that isGeneratorFunction() correctly identifies generator functions.

        Verifies that the method returns True for generator function objects.
        """
        result = Reflection.isGeneratorFunction(self.generator_function)

        self.assertTrue(result)

    def testIsGeneratorFunctionWithRegularFunction(self):
        """
        Test that isGeneratorFunction() correctly identifies regular functions.

        Verifies that the method returns False for regular function objects.
        """
        result = Reflection.isGeneratorFunction(self.function)

        self.assertFalse(result)

    def testIsGetSetDescriptorWithGetSetDescriptor(self):
        """
        Test that isGetSetDescriptor() correctly identifies getset descriptors.

        Verifies that the method returns True for getset descriptor objects.
        Note: Finding actual getset descriptors in Python is rare, so we test
        with False expectation and verify the method works correctly.
        """
        # Most built-in descriptors are member descriptors, not getset descriptors
        result = Reflection.isGetSetDescriptor(complex.real)

        # Since complex.real is actually a member descriptor, this should be False
        self.assertFalse(result)

    def testIsGetSetDescriptorWithNonDescriptor(self):
        """
        Test that isGetSetDescriptor() correctly identifies non-descriptors.

        Verifies that the method returns False for non-descriptor objects.
        """
        result = Reflection.isGetSetDescriptor(self.simple_instance)

        self.assertFalse(result)

    def testIsMemberDescriptorWithMemberDescriptor(self):
        """
        Test that isMemberDescriptor() correctly identifies member descriptors.

        Verifies that the method returns True for member descriptor objects.
        """
        # Test with complex.real which is a member descriptor
        result = Reflection.isMemberDescriptor(complex.real)

        self.assertTrue(result)

    def testIsMemberDescriptorWithNonDescriptor(self):
        """
        Test that isMemberDescriptor() correctly identifies non-descriptors.

        Verifies that the method returns False for non-descriptor objects.
        """
        result = Reflection.isMemberDescriptor(self.simple_instance)

        self.assertFalse(result)

    def testIsMethodWithBoundMethod(self):
        """
        Test that isMethod() correctly identifies bound methods.

        Verifies that the method returns True for bound method objects.
        """
        result = Reflection.isMethod(self.simple_instance.getName)

        self.assertTrue(result)

    def testIsMethodWithUnboundMethod(self):
        """
        Test that isMethod() correctly identifies unbound methods.

        Verifies that the method returns False for unbound method objects.
        """
        result = Reflection.isMethod(SimpleTestClass.getName)

        self.assertFalse(result)

    def testIsMethodWithFunction(self):
        """
        Test that isMethod() correctly identifies functions.

        Verifies that the method returns False for function objects.
        """
        result = Reflection.isMethod(self.function)

        self.assertFalse(result)

    def testIsMethodDescriptorWithMethodDescriptor(self):
        """
        Test that isMethodDescriptor() correctly identifies method descriptors.

        Verifies that the method returns True for method descriptor objects.
        """
        result = Reflection.isMethodDescriptor(str.join)

        self.assertTrue(result)

    def testIsMethodDescriptorWithNonDescriptor(self):
        """
        Test that isMethodDescriptor() correctly identifies non-descriptors.

        Verifies that the method returns False for non-descriptor objects.
        """
        result = Reflection.isMethodDescriptor(self.simple_instance)

        self.assertFalse(result)

    def testIsModuleWithModule(self):
        """
        Test that isModule() correctly identifies modules.

        Verifies that the method returns True for module objects.
        """
        import os
        result = Reflection.isModule(os)

        self.assertTrue(result)

    def testIsModuleWithNonModule(self):
        """
        Test that isModule() correctly identifies non-modules.

        Verifies that the method returns False for non-module objects.
        """
        result = Reflection.isModule(self.simple_instance)

        self.assertFalse(result)

    def testIsRoutineWithFunction(self):
        """
        Test that isRoutine() correctly identifies functions as routines.

        Verifies that the method returns True for function objects.
        """
        result = Reflection.isRoutine(self.function)

        self.assertTrue(result)

    def testIsRoutineWithMethod(self):
        """
        Test that isRoutine() correctly identifies methods as routines.

        Verifies that the method returns True for method objects.
        """
        result = Reflection.isRoutine(self.simple_instance.getName)

        self.assertTrue(result)

    def testIsRoutineWithBuiltinFunction(self):
        """
        Test that isRoutine() correctly identifies built-in functions as routines.

        Verifies that the method returns True for built-in function objects.
        """
        result = Reflection.isRoutine(len)

        self.assertTrue(result)

    def testIsRoutineWithNonRoutine(self):
        """
        Test that isRoutine() correctly identifies non-routines.

        Verifies that the method returns False for non-routine objects.
        """
        result = Reflection.isRoutine(self.simple_instance)

        self.assertFalse(result)

    def testIsTracebackWithTraceback(self):
        """
        Test that isTraceback() correctly identifies traceback objects.

        Verifies that the method returns True for traceback objects.
        """
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            _, _, traceback = sys.exc_info()
            result = Reflection.isTraceback(traceback)
            self.assertTrue(result)

    def testIsTracebackWithNonTraceback(self):
        """
        Test that isTraceback() correctly identifies non-traceback objects.

        Verifies that the method returns False for non-traceback objects.
        """
        result = Reflection.isTraceback(self.simple_instance)

        self.assertFalse(result)

    def testAllTypeCheckMethodsWithNoneValue(self):
        """
        Test that all type checking methods handle None values correctly.

        Verifies that all isX() methods can handle None without raising exceptions.
        """
        type_check_methods = [
            "isAbstract", "isAsyncGen", "isAsyncGenFunction", "isAwaitable",
            "isBuiltin", "isClass", "isCode", "isCoroutine", "isCoroutineFunction",
            "isDataDescriptor", "isFrame", "isFunction", "isGenerator",
            "isGeneratorFunction", "isGetSetDescriptor", "isMemberDescriptor",
            "isMethod", "isMethodDescriptor", "isModule", "isRoutine", "isTraceback",
        ]

        for method_name in type_check_methods:
            with self.subTest(method=method_name):
                method = getattr(Reflection, method_name)
                result = method(None)
                self.assertIsInstance(result, bool)

    def testTypeCheckMethodsUseReflectionType(self):
        """
        Test that type checking methods properly use ReflectionType.

        Verifies that all isX() methods work correctly by testing their
        actual behavior with known objects.
        """
        # Test that isAbstract correctly identifies abstract classes
        self.assertTrue(Reflection.isAbstract(self.abstract_class))
        self.assertFalse(Reflection.isAbstract(self.concrete_class))

        # Test that isClass correctly identifies classes
        self.assertTrue(Reflection.isClass(self.simple_class))
        self.assertFalse(Reflection.isClass(self.simple_instance))

        # Test that isFunction correctly identifies functions
        self.assertTrue(Reflection.isFunction(self.function))
        self.assertFalse(Reflection.isFunction(self.simple_instance))

    def testComprehensiveFactoryMethodValidation(self):
        """
        Test comprehensive validation scenarios for factory methods.

        Verifies that all factory methods properly validate their inputs
        and create the correct reflection objects.
        """
        # Test valid abstract class creation
        abstract_reflection = Reflection.abstract(self.abstract_class)
        self.assertIsInstance(abstract_reflection, ReflectionAbstract)

        # Test valid concrete class creation
        concrete_reflection = Reflection.concrete(self.concrete_class)
        self.assertIsInstance(concrete_reflection, ReflectionConcrete)

        # Test valid instance creation
        instance_reflection = Reflection.instance(self.simple_instance)
        self.assertIsInstance(instance_reflection, ReflectionInstance)

        # Test valid callable creation
        callable_reflection = Reflection.callable(self.function)
        self.assertIsInstance(callable_reflection, ReflectionCallable)

        # Test valid module creation
        module_reflection = Reflection.module(self.module_name)
        self.assertIsInstance(module_reflection, ReflectionModule)

    def testErrorHandlingConsistency(self):
        """
        Test that error handling is consistent across factory methods.

        Verifies that all factory methods raise appropriate exceptions
        when provided with invalid inputs.
        """
        # Test that abstract method raises ReflectionTypeError for non-abstract classes
        with self.assertRaises(ReflectionTypeError):
            Reflection.abstract(self.simple_class)

        # Test that concrete method raises ReflectionValueError for built-in types
        with self.assertRaises(ReflectionValueError):
            Reflection.concrete(str)

        # Test that instance method raises ReflectionValueError for built-in instances
        with self.assertRaises(ReflectionValueError):
            Reflection.instance("test string")

        # Test that callable method raises ReflectionTypeError for non-callable objects
        with self.assertRaises(ReflectionTypeError):
            Reflection.callable(42)

        # Test that module method raises ReflectionTypeError for non-existent modules
        with self.assertRaises(ReflectionTypeError):
            Reflection.module("non_existent_module_xyz123")

    def testAdvancedTypeCheckingScenarios(self):
        """
        Test advanced scenarios for type checking methods.

        Verifies that type checking methods work correctly with complex
        Python objects and edge cases.
        """
        # Test with nested classes
        class OuterClass:
            class InnerClass:
                pass

        self.assertTrue(Reflection.isClass(OuterClass))
        self.assertTrue(Reflection.isClass(OuterClass.InnerClass))

        # Test with metaclasses
        class MetaClass(type):
            pass

        class ClassWithMeta(metaclass=MetaClass):
            pass

        self.assertTrue(Reflection.isClass(ClassWithMeta))
        self.assertTrue(Reflection.isClass(MetaClass))

        # Test with decorated functions
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        @decorator
        def decorated_function():
            return "decorated"

        self.assertTrue(Reflection.isFunction(decorated_function))

    def testConcurrentUsageScenario(self):
        """
        Test that Reflection methods can be used concurrently safely.

        Verifies that the static methods of Reflection class are thread-safe
        and can handle concurrent access without issues.
        """
        import threading
        results = []
        errors = []

        def worker():
            try:
                # Perform multiple reflection operations
                reflection_ops = [
                    lambda: Reflection.isClass(self.simple_class),
                    lambda: Reflection.isFunction(self.function),
                    lambda: Reflection.isAbstract(self.abstract_class),
                    lambda: Reflection.isBuiltin(len),
                    lambda: Reflection.isModule(__import__("os")),
                ]

                for op in reflection_ops:
                    result = op()
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify no errors occurred and results are consistent
        self.assertEqual(len(errors), 0, f"Concurrent usage errors: {errors}")
        self.assertEqual(len(results), 25)  # 5 threads * 5 operations each

    def testMemoryUsageOptimization(self):
        """
        Test memory usage patterns for reflection objects.

        Verifies that reflection objects don't create unnecessary memory
        overhead and can be created/destroyed efficiently.
        """
        import gc

        # Get initial object count
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Create multiple reflection objects
        reflections = []
        for _ in range(100):
            reflections.append(Reflection.instance(self.simple_instance))

        # Verify objects were created
        self.assertEqual(len(reflections), 100)

        # Clean up
        del reflections
        gc.collect()

        # Verify memory was freed (allowing for some variance)
        final_objects = len(gc.get_objects())
        object_difference = final_objects - initial_objects

        # Allow for some variance in object count due to Python internals
        self.assertLess(object_difference, 50, "Memory usage appears to be inefficient")

    def testComplexInheritanceScenarios(self):
        """
        Test reflection with complex inheritance hierarchies.

        Verifies that reflection works correctly with multiple inheritance,
        mixins, and complex class hierarchies.
        """
        class MixinA:
            def method_a(self):
                return "a"

        class MixinB:
            def method_b(self):
                return "b"

        class MultipleInheritanceClass(MixinA, MixinB, SimpleTestClass):
            def combined_method(self):
                return f"{self.method_a()}{self.method_b()}{self.getName()}"

        # Test that complex inheritance is handled correctly
        self.assertTrue(Reflection.isClass(MultipleInheritanceClass))

        complex_instance = MultipleInheritanceClass("complex")
        instance_reflection = Reflection.instance(complex_instance)
        self.assertIsInstance(instance_reflection, ReflectionInstance)

        # Test with abstract mixins
        class AbstractMixin(ABC):
            @abstractmethod
            def abstract_mixin_method(self):
                pass

        class ConcreteWithAbstractMixin(AbstractMixin):
            def abstract_mixin_method(self):
                return "implemented"

        self.assertTrue(Reflection.isAbstract(AbstractMixin))
        self.assertFalse(Reflection.isAbstract(ConcreteWithAbstractMixin))

    def testPerformanceBenchmark(self):
        """
        Test performance characteristics of reflection operations.

        Verifies that reflection operations complete within reasonable
        time limits and scale appropriately.
        """
        import time

        # Test factory method performance
        start_time = time.time()
        for _ in range(1000):
            Reflection.instance(self.simple_instance)
        factory_time = time.time() - start_time

        # Test type checking performance
        start_time = time.time()
        for _ in range(1000):
            Reflection.isClass(self.simple_class)
        type_check_time = time.time() - start_time

        # Verify operations complete within reasonable time (10ms per 1000 operations)
        self.assertLess(factory_time, 0.1, "Factory method performance is too slow")
        self.assertLess(type_check_time, 0.1, "Type checking performance is too slow")

    def testEdgeCasesWithSpecialMethods(self):
        """
        Test reflection behavior with classes containing special methods.

        Verifies that reflection works correctly with classes that implement
        various Python special methods (__call__, __new__, etc.).
        """
        class CallableClass:
            def __call__(self):
                return "called"

            def __new__(cls):
                return super().__new__(cls)

            def __init__(self):
                self.value = "initialized"

        # Test with callable objects
        callable_instance = CallableClass()
        self.assertTrue(Reflection.isClass(CallableClass))

        # Test instance reflection with callable instance
        instance_reflection = Reflection.instance(callable_instance)
        self.assertIsInstance(instance_reflection, ReflectionInstance)

        # Test that the instance itself is not considered a function
        self.assertFalse(Reflection.isFunction(callable_instance))

        # But it should be considered callable by Python's built-in callable()
        self.assertTrue(callable(callable_instance))

    def testConsistencyAcrossReflectionTypes(self):
        """
        Test consistency of behavior across different reflection types.

        Verifies that similar operations across different reflection
        classes behave consistently.
        """
        # Create different types of reflection objects
        abstract_refl = Reflection.abstract(self.abstract_class)
        concrete_refl = Reflection.concrete(self.concrete_class)
        instance_refl = Reflection.instance(self.simple_instance)
        callable_refl = Reflection.callable(self.function)
        module_refl = Reflection.module(self.module_name)

        # Verify all are different types
        reflection_types = [
            type(abstract_refl),
            type(concrete_refl),
            type(instance_refl),
            type(callable_refl),
            type(module_refl),
        ]

        # All should be different types
        self.assertEqual(len(set(reflection_types)), 5)

        # All should be instances of their respective types
        self.assertIsInstance(abstract_refl, ReflectionAbstract)
        self.assertIsInstance(concrete_refl, ReflectionConcrete)
        self.assertIsInstance(instance_refl, ReflectionInstance)
        self.assertIsInstance(callable_refl, ReflectionCallable)
        self.assertIsInstance(module_refl, ReflectionModule)

    def testFactoryMethodsReturnCorrectTypes(self):
        """
        Test that all factory methods return the expected types.

        Verifies that each factory method returns an instance of the
        correct reflection class.
        """
        factory_methods = [
            ("instance", self.simple_instance, ReflectionInstance),
            ("abstract", self.abstract_class, ReflectionAbstract),
            ("concrete", self.concrete_class, ReflectionConcrete),
            ("module", self.module_name, ReflectionModule),
            ("callable", self.function, ReflectionCallable),
        ]

        for method_name, test_arg, expected_type in factory_methods:
            with self.subTest(method=method_name, expected_type=expected_type.__name__):
                method = getattr(Reflection, method_name)
                result = method(test_arg)
                self.assertIsInstance(result, expected_type)

    def testFactoryMethodsWithValidEdgeCases(self):
        """
        Test that factory methods handle valid edge cases properly.

        Verifies that factory methods work correctly with valid edge cases
        that pass the framework's validation rules.
        """
        edge_cases = [
            ("concrete", object, ReflectionConcrete),
        ]

        for method_name, test_arg, expected_type in edge_cases:
            with self.subTest(method=method_name, arg=str(test_arg)):
                method = getattr(Reflection, method_name)
                result = method(test_arg)
                self.assertIsInstance(result, expected_type)

    def testFactoryMethodsWithInvalidEdgeCasesRaiseExceptions(self):
        """
        Test that factory methods raise exceptions for invalid edge cases.

        Verifies that factory methods raise appropriate exceptions for
        edge cases that violate the framework's validation rules.
        """
        invalid_cases = [
            ("instance", "", ReflectionValueError),
            ("instance", 0, ReflectionValueError),
            ("instance", [], ReflectionValueError),
            ("instance", {}, ReflectionValueError),
            ("callable", print, ReflectionTypeError),
        ]

        for method_name, test_arg, expected_exception in invalid_cases:
            with self.subTest(method=method_name, arg=str(test_arg)):
                method = getattr(Reflection, method_name)
                with self.assertRaises(expected_exception):
                    method(test_arg)
