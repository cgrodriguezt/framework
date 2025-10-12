import inspect
import asyncio
from typing import Any, Dict
from abc import ABC, abstractmethod
from orionis.services.introspection.objects.types import Type
from orionis.test.cases.synchronous import SyncTestCase

class AbstractTestClass(ABC):
    """Abstract class for testing abstract type detection."""

    @abstractmethod
    def abstract_method(self):
        """Abstract method for testing purposes."""
        pass

class ConcreteTestClass(AbstractTestClass):
    """Concrete class for testing class type detection."""

    def abstract_method(self):
        """Implementation of abstract method."""
        return "implemented"

    def regular_method(self):
        """Regular method for testing method detection."""
        return "regular"

    @property
    def test_property(self):
        """Property for testing descriptor detection."""
        return "property_value"

    @test_property.setter
    def test_property(self, value):
        """Property setter for testing descriptor detection."""
        self._test_property = value

def test_function():
    """Regular function for testing function detection."""
    return "function"

def test_generator_function():
    """Generator function for testing generator detection."""
    yield 1
    yield 2
    yield 3

async def test_async_function():
    """Async function for testing coroutine function detection."""
    await asyncio.sleep(0.001)
    return "async_result"

async def test_async_generator_function():
    """Async generator function for testing async generator detection."""
    yield 1
    await asyncio.sleep(0.001)
    yield 2

class TestReflectionType(SyncTestCase):

    def setUp(self) -> None:
        """
        Set up comprehensive test environment with various object types.

        Initializes a comprehensive collection of Python objects including
        classes, instances, functions, generators, coroutines, modules,
        descriptors, and built-in types. This collection serves as the
        foundation for testing all Type class methods.

        Notes
        -----
        The test_objects dictionary is organized by category:
        - Classes: Abstract and concrete classes
        - Instances: Class instances and built-in instances
        - Functions: Regular, generator, async, and built-in functions
        - Objects: Generators, coroutines, code objects, frames
        - Descriptors: Properties, methods, and various descriptor types
        - Built-ins: Modules, built-in functions, and primitive types
        """
        # Create instances for testing
        concrete_instance = ConcreteTestClass()
        generator_instance = test_generator_function()
        async_generator_instance = test_async_generator_function()
        coroutine_instance = test_async_function()

        # Get frame object for testing
        frame_object = inspect.currentframe()

        self.test_objects: Dict[str, Any] = {
            # Abstract and concrete classes
            "abstract_class": AbstractTestClass,
            "concrete_class": ConcreteTestClass,
            "concrete_instance": concrete_instance,

            # Functions and methods
            "regular_function": test_function,
            "generator_function": test_generator_function,
            "async_function": test_async_function,
            "async_generator_function": test_async_generator_function,
            "builtin_function": len,
            "builtin_method": "test".upper,  # This is actually a builtin function, not method
            "instance_method": concrete_instance.regular_method,
            "bound_method": concrete_instance.regular_method,

            # Generator and async objects
            "generator_object": generator_instance,
            "async_generator_object": async_generator_instance,
            "coroutine_object": coroutine_instance,

            # Code and frame objects
            "code_object": test_function.__code__,
            "frame_object": frame_object,

            # Descriptors and properties
            "property_descriptor": ConcreteTestClass.test_property,
            "method_descriptor": str.upper,

            # Built-in types and primitives
            "module_object": inspect,
            "integer": 42,
            "string": "test_string",
            "list_object": [1, 2, 3],
            "dict_object": {"key": "value"},

            # Special objects
            "none_object": None,
            "type_object": type,
            "lambda_function": lambda x: x + 1,
        }

    def tearDown(self) -> None:
        """
        Clean up test resources after each test method completion.

        Properly closes any coroutine objects to avoid runtime warnings
        and resets the test_objects dictionary to prevent memory leaks
        between test method executions.
        """
        # Close coroutine to avoid warnings
        if hasattr(self.test_objects.get("coroutine_object"), "close"):
            self.test_objects["coroutine_object"].close()

        # Close async generator to avoid warnings
        async_gen = self.test_objects.get("async_generator_object")
        if hasattr(async_gen, "aclose"):
            try:
                # Create a simple event loop to close the async generator
                import asyncio
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    try:
                        asyncio.run(async_gen.aclose())
                    except RuntimeError:
                        # If there's already a loop running, ignore
                        pass
            except Exception:
                pass

        self.test_objects = None

    def testIsAbstract(self) -> None:
        """
        Test abstract base class detection functionality.

        Validates that the isAbstract method correctly identifies abstract
        base classes (ABC) while distinguishing them from concrete classes,
        instances, and non-class objects. Tests both positive and negative
        cases to ensure accurate abstract class detection.

        The method should return True only for classes that inherit from ABC
        and contain at least one abstract method, False for all other objects.

        Raises
        ------
        AssertionError
            If abstract class detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(AbstractTestClass)
        >>> type_checker.isAbstract()  # True
        >>> type_checker = Type(ConcreteTestClass)
        >>> type_checker.isAbstract()  # False
        """
        # Test abstract class detection
        abstract_type = Type(self.test_objects["abstract_class"])
        self.assertTrue(abstract_type.isAbstract(),
                       "Abstract class should be detected as abstract")

        # Test concrete class should not be abstract
        concrete_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(concrete_type.isAbstract(),
                        "Concrete class should not be detected as abstract")

        # Test instance should not be abstract
        instance_type = Type(self.test_objects["concrete_instance"])
        self.assertFalse(instance_type.isAbstract(),
                        "Instance should not be detected as abstract")

        # Test non-class objects should not be abstract
        function_type = Type(self.test_objects["regular_function"])
        self.assertFalse(function_type.isAbstract(),
                        "Function should not be detected as abstract")

        module_type = Type(self.test_objects["module_object"])
        self.assertFalse(module_type.isAbstract(),
                        "Module should not be detected as abstract")

    def testIsAsyncGen(self) -> None:
        """
        Test asynchronous generator object detection functionality.

        Validates that the isAsyncGen method correctly identifies asynchronous
        generator objects while distinguishing them from regular generators,
        async generator functions, and other object types.

        The method should return True only for actual async generator objects
        (not the functions that create them), False for all other objects.

        Raises
        ------
        AssertionError
            If async generator detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> async_gen = test_async_generator_function()
        >>> type_checker = Type(async_gen)
        >>> type_checker.isAsyncGen()  # True
        """
        # Test async generator object detection
        async_gen_type = Type(self.test_objects["async_generator_object"])
        self.assertTrue(async_gen_type.isAsyncGen(),
                       "Async generator object should be detected as async generator")

        # Test regular generator should not be async generator
        gen_type = Type(self.test_objects["generator_object"])
        self.assertFalse(gen_type.isAsyncGen(),
                        "Regular generator should not be detected as async generator")

        # Test async generator function should not be async generator object
        async_gen_func_type = Type(self.test_objects["async_generator_function"])
        self.assertFalse(async_gen_func_type.isAsyncGen(),
                        "Async generator function should not be detected as async generator object")

        # Test other objects should not be async generators
        function_type = Type(self.test_objects["regular_function"])
        self.assertFalse(function_type.isAsyncGen(),
                        "Regular function should not be detected as async generator")

        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isAsyncGen(),
                        "Class should not be detected as async generator")

    def testIsAsyncGenFunction(self) -> None:
        """
        Test asynchronous generator function detection functionality.

        Validates that the isAsyncGenFunction method correctly identifies
        asynchronous generator functions while distinguishing them from
        async generator objects, regular functions, and other object types.

        The method should return True only for functions defined with
        'async def' that contain 'yield' statements, False for all other objects.

        Raises
        ------
        AssertionError
            If async generator function detection produces incorrect results
            for any tested object type.

        Examples
        --------
        >>> type_checker = Type(test_async_generator_function)
        >>> type_checker.isAsyncGenFunction()  # True
        """
        # Test async generator function detection
        async_gen_func_type = Type(self.test_objects["async_generator_function"])
        self.assertTrue(async_gen_func_type.isAsyncGenFunction(),
                       "Async generator function should be detected as async generator function")

        # Test regular generator function should not be async generator function
        gen_func_type = Type(self.test_objects["generator_function"])
        self.assertFalse(gen_func_type.isAsyncGenFunction(),
                        "Regular generator function should not be detected as async generator function")

        # Test async function should not be async generator function
        async_func_type = Type(self.test_objects["async_function"])
        self.assertFalse(async_func_type.isAsyncGenFunction(),
                        "Async function should not be detected as async generator function")

        # Test regular function should not be async generator function
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isAsyncGenFunction(),
                        "Regular function should not be detected as async generator function")

        # Test non-function objects should not be async generator functions
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isAsyncGenFunction(),
                        "Class should not be detected as async generator function")

    def testIsAwaitable(self) -> None:
        """
        Test awaitable object detection functionality.

        Validates that the isAwaitable method correctly identifies objects
        that can be awaited (coroutines, tasks, futures) while distinguishing
        them from non-awaitable objects like functions, classes, and primitives.

        The method should return True for coroutine objects and other awaitable
        types, False for all non-awaitable objects.

        Raises
        ------
        AssertionError
            If awaitable detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> coroutine = test_async_function()
        >>> type_checker = Type(coroutine)
        >>> type_checker.isAwaitable()  # True
        """
        # Test coroutine object is awaitable
        coroutine_type = Type(self.test_objects["coroutine_object"])
        self.assertTrue(coroutine_type.isAwaitable(),
                       "Coroutine object should be detected as awaitable")

        # Test async function is not awaitable (only when called)
        async_func_type = Type(self.test_objects["async_function"])
        self.assertFalse(async_func_type.isAwaitable(),
                        "Async function should not be detected as awaitable")

        # Test regular function is not awaitable
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isAwaitable(),
                        "Regular function should not be detected as awaitable")

        # Test other objects are not awaitable
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isAwaitable(),
                        "Class should not be detected as awaitable")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isAwaitable(),
                        "Integer should not be detected as awaitable")

    def testIsBuiltin(self) -> None:
        """
        Test built-in function detection functionality.

        Validates that the isBuiltin method correctly identifies built-in
        functions and methods while distinguishing them from user-defined
        functions, classes, and other object types.

        The method should return True for built-in functions like len, print,
        and built-in methods, False for user-defined functions and other objects.

        Raises
        ------
        AssertionError
            If built-in function detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(len)
        >>> type_checker.isBuiltin()  # True
        >>> type_checker = Type(test_function)
        >>> type_checker.isBuiltin()  # False
        """
        # Test built-in function detection
        builtin_func_type = Type(self.test_objects["builtin_function"])
        self.assertTrue(builtin_func_type.isBuiltin(),
                       "Built-in function should be detected as built-in")

        # Test user-defined function should not be built-in
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isBuiltin(),
                        "User-defined function should not be detected as built-in")

        # Test lambda function should not be built-in
        lambda_type = Type(self.test_objects["lambda_function"])
        self.assertFalse(lambda_type.isBuiltin(),
                        "Lambda function should not be detected as built-in")

        # Test other objects should not be built-in
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isBuiltin(),
                        "Class should not be detected as built-in")

        instance_type = Type(self.test_objects["concrete_instance"])
        self.assertFalse(instance_type.isBuiltin(),
                        "Instance should not be detected as built-in")

    def testIsClass(self) -> None:
        """
        Test class type detection functionality.

        Validates that the isClass method correctly identifies class objects
        while distinguishing them from class instances, functions, modules,
        and other object types.

        The method should return True only for class objects (both user-defined
        and built-in classes), False for instances and other object types.

        Raises
        ------
        AssertionError
            If class detection produces incorrect results for any tested
            object type.

        Examples
        --------
        >>> type_checker = Type(ConcreteTestClass)
        >>> type_checker.isClass()  # True
        >>> instance = ConcreteTestClass()
        >>> type_checker = Type(instance)
        >>> type_checker.isClass()  # False
        """
        # Test class detection
        class_type = Type(self.test_objects["concrete_class"])
        self.assertTrue(class_type.isClass(),
                       "Class should be detected as class")

        abstract_class_type = Type(self.test_objects["abstract_class"])
        self.assertTrue(abstract_class_type.isClass(),
                       "Abstract class should be detected as class")

        # Test built-in class detection
        type_class_type = Type(self.test_objects["type_object"])
        self.assertTrue(type_class_type.isClass(),
                       "Built-in type class should be detected as class")

        # Test instance should not be class
        instance_type = Type(self.test_objects["concrete_instance"])
        self.assertFalse(instance_type.isClass(),
                        "Instance should not be detected as class")

        # Test other objects should not be classes
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isClass(),
                        "Function should not be detected as class")

        module_type = Type(self.test_objects["module_object"])
        self.assertFalse(module_type.isClass(),
                        "Module should not be detected as class")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isClass(),
                        "Integer should not be detected as class")

    def testIsCode(self) -> None:
        """
        Test code object detection functionality.

        Validates that the isCode method correctly identifies code objects
        while distinguishing them from functions, classes, and other object types.

        The method should return True only for code objects (accessible via
        __code__ attribute of functions), False for all other object types.

        Raises
        ------
        AssertionError
            If code object detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(test_function.__code__)
        >>> type_checker.isCode()  # True
        >>> type_checker = Type(test_function)
        >>> type_checker.isCode()  # False
        """
        # Test code object detection
        code_type = Type(self.test_objects["code_object"])
        self.assertTrue(code_type.isCode(),
                       "Code object should be detected as code")

        # Test function should not be code object
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isCode(),
                        "Function should not be detected as code object")

        # Test other objects should not be code objects
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isCode(),
                        "Class should not be detected as code object")

        instance_type = Type(self.test_objects["concrete_instance"])
        self.assertFalse(instance_type.isCode(),
                        "Instance should not be detected as code object")

        module_type = Type(self.test_objects["module_object"])
        self.assertFalse(module_type.isCode(),
                        "Module should not be detected as code object")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isCode(),
                        "Integer should not be detected as code object")

    def testIsCoroutine(self) -> None:
        """
        Test coroutine object detection functionality.

        Validates that the isCoroutine method correctly identifies coroutine
        objects while distinguishing them from coroutine functions, regular
        functions, and other object types.

        The method should return True only for actual coroutine objects
        (created by calling async functions), False for coroutine functions
        and other object types.

        Raises
        ------
        AssertionError
            If coroutine detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> coroutine = test_async_function()
        >>> type_checker = Type(coroutine)
        >>> type_checker.isCoroutine()  # True
        """
        # Test coroutine object detection
        coroutine_type = Type(self.test_objects["coroutine_object"])
        self.assertTrue(coroutine_type.isCoroutine(),
                       "Coroutine object should be detected as coroutine")

        # Test async function should not be coroutine object
        async_func_type = Type(self.test_objects["async_function"])
        self.assertFalse(async_func_type.isCoroutine(),
                        "Async function should not be detected as coroutine object")

        # Test regular function should not be coroutine
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isCoroutine(),
                        "Regular function should not be detected as coroutine")

        # Test other objects should not be coroutines
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isCoroutine(),
                        "Class should not be detected as coroutine")

        generator_type = Type(self.test_objects["generator_object"])
        self.assertFalse(generator_type.isCoroutine(),
                        "Generator should not be detected as coroutine")

    def testIsCoroutineFunction(self) -> None:
        """
        Test coroutine function detection functionality.

        Validates that the isCoroutineFunction method correctly identifies
        coroutine functions (async def) while distinguishing them from
        coroutine objects, regular functions, and other object types.

        The method should return True only for functions defined with 'async def',
        False for coroutine objects and other object types.

        Raises
        ------
        AssertionError
            If coroutine function detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(test_async_function)
        >>> type_checker.isCoroutineFunction()  # True
        """
        # Test async function detection
        async_func_type = Type(self.test_objects["async_function"])
        self.assertTrue(async_func_type.isCoroutineFunction(),
                       "Async function should be detected as coroutine function")

        # Test regular function should not be coroutine function
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isCoroutineFunction(),
                        "Regular function should not be detected as coroutine function")

        # Test coroutine object should not be coroutine function
        coroutine_type = Type(self.test_objects["coroutine_object"])
        self.assertFalse(coroutine_type.isCoroutineFunction(),
                        "Coroutine object should not be detected as coroutine function")

        # Test other objects should not be coroutine functions
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isCoroutineFunction(),
                        "Class should not be detected as coroutine function")

        builtin_func_type = Type(self.test_objects["builtin_function"])
        self.assertFalse(builtin_func_type.isCoroutineFunction(),
                        "Built-in function should not be detected as coroutine function")

    def testIsDataDescriptor(self) -> None:
        """
        Test data descriptor detection functionality.

        Validates that the isDataDescriptor method correctly identifies data
        descriptors (objects with both __get__ and __set__ methods) while
        distinguishing them from non-data descriptors and regular objects.

        The method should return True for properties and other data descriptors,
        False for method descriptors and regular objects.

        Raises
        ------
        AssertionError
            If data descriptor detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(ConcreteTestClass.test_property)
        >>> type_checker.isDataDescriptor()  # True
        """
        # Test property descriptor is data descriptor
        property_type = Type(self.test_objects["property_descriptor"])
        self.assertTrue(property_type.isDataDescriptor(),
                       "Property should be detected as data descriptor")

        # Test method descriptor should not be data descriptor
        method_desc_type = Type(self.test_objects["method_descriptor"])
        self.assertFalse(method_desc_type.isDataDescriptor(),
                        "Method descriptor should not be detected as data descriptor")

        # Test regular objects should not be data descriptors
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isDataDescriptor(),
                        "Function should not be detected as data descriptor")

        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isDataDescriptor(),
                        "Class should not be detected as data descriptor")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isDataDescriptor(),
                        "Integer should not be detected as data descriptor")

    def testIsFrame(self) -> None:
        """
        Test frame object detection functionality.

        Validates that the isFrame method correctly identifies frame objects
        while distinguishing them from other object types.

        The method should return True only for frame objects (execution frames),
        False for all other object types.

        Raises
        ------
        AssertionError
            If frame object detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> frame = inspect.currentframe()
        >>> type_checker = Type(frame)
        >>> type_checker.isFrame()  # True
        """
        # Test frame object detection
        if self.test_objects["frame_object"] is not None:
            frame_type = Type(self.test_objects["frame_object"])
            self.assertTrue(frame_type.isFrame(),
                           "Frame object should be detected as frame")

        # Test other objects should not be frames
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isFrame(),
                        "Function should not be detected as frame")

        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isFrame(),
                        "Class should not be detected as frame")

        code_type = Type(self.test_objects["code_object"])
        self.assertFalse(code_type.isFrame(),
                        "Code object should not be detected as frame")

        module_type = Type(self.test_objects["module_object"])
        self.assertFalse(module_type.isFrame(),
                        "Module should not be detected as frame")

    def testIsFunction(self) -> None:
        """
        Test Python function detection functionality.

        Validates that the isFunction method correctly identifies Python
        functions while distinguishing them from built-in functions,
        methods, classes, and other object types.

        The method should return True only for user-defined Python functions,
        False for built-in functions, methods, and other object types.

        Raises
        ------
        AssertionError
            If function detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(test_function)
        >>> type_checker.isFunction()  # True
        >>> type_checker = Type(len)
        >>> type_checker.isFunction()  # False
        """
        # Test user-defined function detection
        func_type = Type(self.test_objects["regular_function"])
        self.assertTrue(func_type.isFunction(),
                       "Regular function should be detected as function")

        async_func_type = Type(self.test_objects["async_function"])
        self.assertTrue(async_func_type.isFunction(),
                       "Async function should be detected as function")

        lambda_type = Type(self.test_objects["lambda_function"])
        self.assertTrue(lambda_type.isFunction(),
                       "Lambda function should be detected as function")

        # Test built-in function should not be detected as Python function
        builtin_func_type = Type(self.test_objects["builtin_function"])
        self.assertFalse(builtin_func_type.isFunction(),
                        "Built-in function should not be detected as Python function")

        # Test other objects should not be functions
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isFunction(),
                        "Class should not be detected as function")

        method_type = Type(self.test_objects["bound_method"])
        self.assertFalse(method_type.isFunction(),
                        "Bound method should not be detected as function")

        module_type = Type(self.test_objects["module_object"])
        self.assertFalse(module_type.isFunction(),
                        "Module should not be detected as function")

    def testIsGenerator(self) -> None:
        """
        Test generator object detection functionality.

        Validates that the isGenerator method correctly identifies generator
        objects while distinguishing them from generator functions, async
        generators, and other object types.

        The method should return True only for actual generator objects
        (created by calling generator functions), False for generator
        functions and other object types.

        Raises
        ------
        AssertionError
            If generator detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> gen = test_generator_function()
        >>> type_checker = Type(gen)
        >>> type_checker.isGenerator()  # True
        """
        # Test generator object detection
        gen_type = Type(self.test_objects["generator_object"])
        self.assertTrue(gen_type.isGenerator(),
                       "Generator object should be detected as generator")

        # Test generator function should not be generator object
        gen_func_type = Type(self.test_objects["generator_function"])
        self.assertFalse(gen_func_type.isGenerator(),
                        "Generator function should not be detected as generator object")

        # Test async generator should not be regular generator
        async_gen_type = Type(self.test_objects["async_generator_object"])
        self.assertFalse(async_gen_type.isGenerator(),
                        "Async generator should not be detected as regular generator")

        # Test other objects should not be generators
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isGenerator(),
                        "Regular function should not be detected as generator")

        coroutine_type = Type(self.test_objects["coroutine_object"])
        self.assertFalse(coroutine_type.isGenerator(),
                        "Coroutine should not be detected as generator")

    def testIsGeneratorFunction(self) -> None:
        """
        Test generator function detection functionality.

        Validates that the isGeneratorFunction method correctly identifies
        generator functions while distinguishing them from generator objects,
        async generator functions, and other object types.

        The method should return True only for functions that contain 'yield'
        statements, False for generator objects and other object types.

        Raises
        ------
        AssertionError
            If generator function detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(test_generator_function)
        >>> type_checker.isGeneratorFunction()  # True
        """
        # Test generator function detection
        gen_func_type = Type(self.test_objects["generator_function"])
        self.assertTrue(gen_func_type.isGeneratorFunction(),
                       "Generator function should be detected as generator function")

        # Test regular function should not be generator function
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isGeneratorFunction(),
                        "Regular function should not be detected as generator function")

        # Test async generator function should not be regular generator function
        async_gen_func_type = Type(self.test_objects["async_generator_function"])
        self.assertFalse(async_gen_func_type.isGeneratorFunction(),
                        "Async generator function should not be detected as regular generator function")

        # Test generator object should not be generator function
        gen_type = Type(self.test_objects["generator_object"])
        self.assertFalse(gen_type.isGeneratorFunction(),
                        "Generator object should not be detected as generator function")

        # Test other objects should not be generator functions
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isGeneratorFunction(),
                        "Class should not be detected as generator function")

    def testIsGetSetDescriptor(self) -> None:
        """
        Test getset descriptor detection functionality.

        Validates that the isGetSetDescriptor method correctly identifies
        getset descriptors while distinguishing them from other descriptor
        types and regular objects.

        The method should return True for getset descriptors (typically
        built-in attribute access descriptors), False for other object types.

        Raises
        ------
        AssertionError
            If getset descriptor detection produces incorrect results for any
            tested object type.

        Notes
        -----
        Getset descriptors are typically internal C-level descriptors and
        may not be commonly encountered in regular Python code.
        """
        # Test that regular objects are not getset descriptors
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isGetSetDescriptor(),
                        "Function should not be detected as getset descriptor")

        property_type = Type(self.test_objects["property_descriptor"])
        self.assertFalse(property_type.isGetSetDescriptor(),
                        "Property should not be detected as getset descriptor")

        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isGetSetDescriptor(),
                        "Class should not be detected as getset descriptor")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isGetSetDescriptor(),
                        "Integer should not be detected as getset descriptor")

        # Note: Getset descriptors are typically internal and hard to create
        # in tests, so we mainly test negative cases

    def testIsMemberDescriptor(self) -> None:
        """
        Test member descriptor detection functionality.

        Validates that the isMemberDescriptor method correctly identifies
        member descriptors while distinguishing them from other descriptor
        types and regular objects.

        The method should return True for member descriptors (typically
        used for instance variables in C extensions), False for other object types.

        Raises
        ------
        AssertionError
            If member descriptor detection produces incorrect results for any
            tested object type.

        Notes
        -----
        Member descriptors are typically internal C-level descriptors and
        may not be commonly encountered in regular Python code.
        """
        # Test that regular objects are not member descriptors
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isMemberDescriptor(),
                        "Function should not be detected as member descriptor")

        property_type = Type(self.test_objects["property_descriptor"])
        self.assertFalse(property_type.isMemberDescriptor(),
                        "Property should not be detected as member descriptor")

        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isMemberDescriptor(),
                        "Class should not be detected as member descriptor")

        method_desc_type = Type(self.test_objects["method_descriptor"])
        self.assertFalse(method_desc_type.isMemberDescriptor(),
                        "Method descriptor should not be detected as member descriptor")

        # Note: Member descriptors are typically internal and hard to create
        # in tests, so we mainly test negative cases

    def testIsMethod(self) -> None:
        """
        Test method detection functionality.

        Validates that the isMethod method correctly identifies bound methods
        while distinguishing them from unbound functions, built-in functions,
        classes, and other object types.

        The method should return True only for bound methods (methods called
        on instances), False for functions, built-in functions and other object types.
        Note that built-in methods like str.upper are classified as built-in functions,
        not methods in the strict sense of inspect.ismethod().

        Raises
        ------
        AssertionError
            If method detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> instance = ConcreteTestClass()
        >>> type_checker = Type(instance.regular_method)
        >>> type_checker.isMethod()  # True
        >>> type_checker = Type("test".upper)
        >>> type_checker.isMethod()  # False (it's a builtin function)
        """
        # Test bound method detection
        method_type = Type(self.test_objects["bound_method"])
        self.assertTrue(method_type.isMethod(),
                       "Bound method should be detected as method")

        # Test built-in method detection (Note: builtin methods like str.upper are builtin functions, not methods)
        builtin_method_type = Type(self.test_objects["builtin_method"])
        self.assertFalse(builtin_method_type.isMethod(),
                        "Built-in function should not be detected as method (it's a builtin function)")

        # Test regular function should not be method
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isMethod(),
                        "Regular function should not be detected as method")

        # Test lambda should not be method
        lambda_type = Type(self.test_objects["lambda_function"])
        self.assertFalse(lambda_type.isMethod(),
                        "Lambda function should not be detected as method")

        # Test other objects should not be methods
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isMethod(),
                        "Class should not be detected as method")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isMethod(),
                        "Integer should not be detected as method")

    def testIsMethodDescriptor(self) -> None:
        """
        Test method descriptor detection functionality.

        Validates that the isMethodDescriptor method correctly identifies
        method descriptors while distinguishing them from data descriptors,
        bound methods, and other object types.

        The method should return True for method descriptors (unbound methods
        in classes), False for bound methods and other object types.

        Raises
        ------
        AssertionError
            If method descriptor detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(str.upper)
        >>> type_checker.isMethodDescriptor()  # True
        """
        # Test method descriptor detection
        method_desc_type = Type(self.test_objects["method_descriptor"])
        self.assertTrue(method_desc_type.isMethodDescriptor(),
                       "Method descriptor should be detected as method descriptor")

        # Test bound method should not be method descriptor
        method_type = Type(self.test_objects["bound_method"])
        self.assertFalse(method_type.isMethodDescriptor(),
                        "Bound method should not be detected as method descriptor")

        # Test property should not be method descriptor
        property_type = Type(self.test_objects["property_descriptor"])
        self.assertFalse(property_type.isMethodDescriptor(),
                        "Property should not be detected as method descriptor")

        # Test regular function should not be method descriptor
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isMethodDescriptor(),
                        "Regular function should not be detected as method descriptor")

        # Test other objects should not be method descriptors
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isMethodDescriptor(),
                        "Class should not be detected as method descriptor")

    def testIsModule(self) -> None:
        """
        Test module detection functionality.

        Validates that the isModule method correctly identifies module objects
        while distinguishing them from classes, functions, and other object types.

        The method should return True only for module objects, False for all
        other object types including classes and instances.

        Raises
        ------
        AssertionError
            If module detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> import inspect
        >>> type_checker = Type(inspect)
        >>> type_checker.isModule()  # True
        """
        # Test module detection
        module_type = Type(self.test_objects["module_object"])
        self.assertTrue(module_type.isModule(),
                       "Module should be detected as module")

        # Test other objects should not be modules
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isModule(),
                        "Class should not be detected as module")

        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isModule(),
                        "Function should not be detected as module")

        instance_type = Type(self.test_objects["concrete_instance"])
        self.assertFalse(instance_type.isModule(),
                        "Instance should not be detected as module")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isModule(),
                        "Integer should not be detected as module")

        string_type = Type(self.test_objects["string"])
        self.assertFalse(string_type.isModule(),
                        "String should not be detected as module")

    def testIsRoutine(self) -> None:
        """
        Test routine detection functionality.

        Validates that the isRoutine method correctly identifies routines
        (user-defined or built-in functions and methods) while distinguishing
        them from classes, modules, and other object types.

        The method should return True for functions, methods, and built-in
        callables, False for non-callable objects.

        Raises
        ------
        AssertionError
            If routine detection produces incorrect results for any
            tested object type.

        Examples
        --------
        >>> type_checker = Type(test_function)
        >>> type_checker.isRoutine()  # True
        >>> type_checker = Type(len)
        >>> type_checker.isRoutine()  # True
        """
        # Test that functions are routines
        func_type = Type(self.test_objects["regular_function"])
        self.assertTrue(func_type.isRoutine(),
                       "Function should be detected as routine")

        async_func_type = Type(self.test_objects["async_function"])
        self.assertTrue(async_func_type.isRoutine(),
                       "Async function should be detected as routine")

        lambda_type = Type(self.test_objects["lambda_function"])
        self.assertTrue(lambda_type.isRoutine(),
                       "Lambda function should be detected as routine")

        # Test that built-in functions are routines
        builtin_func_type = Type(self.test_objects["builtin_function"])
        self.assertTrue(builtin_func_type.isRoutine(),
                       "Built-in function should be detected as routine")

        # Test that methods are routines
        method_type = Type(self.test_objects["bound_method"])
        self.assertTrue(method_type.isRoutine(),
                       "Bound method should be detected as routine")

        builtin_method_type = Type(self.test_objects["builtin_method"])
        self.assertTrue(builtin_method_type.isRoutine(),
                       "Built-in method should be detected as routine")

        # Test that non-callable objects are not routines
        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isRoutine(),
                        "Class should not be detected as routine")

        instance_type = Type(self.test_objects["concrete_instance"])
        self.assertFalse(instance_type.isRoutine(),
                        "Instance should not be detected as routine")

        integer_type = Type(self.test_objects["integer"])
        self.assertFalse(integer_type.isRoutine(),
                        "Integer should not be detected as routine")

        module_type = Type(self.test_objects["module_object"])
        self.assertFalse(module_type.isRoutine(),
                        "Module should not be detected as routine")

    def testIsTraceback(self) -> None:
        """
        Test traceback object detection functionality.

        Validates that the isTraceback method correctly identifies traceback
        objects while distinguishing them from other object types.

        The method should return True only for traceback objects (created
        during exception handling), False for all other object types.

        Raises
        ------
        AssertionError
            If traceback detection produces incorrect results for any
            tested object type.

        Notes
        -----
        Traceback objects are typically created during exception handling
        and are difficult to create directly in tests, so this test mainly
        validates negative cases.
        """
        # Test that regular objects are not tracebacks
        func_type = Type(self.test_objects["regular_function"])
        self.assertFalse(func_type.isTraceback(),
                        "Function should not be detected as traceback")

        class_type = Type(self.test_objects["concrete_class"])
        self.assertFalse(class_type.isTraceback(),
                        "Class should not be detected as traceback")

        instance_type = Type(self.test_objects["concrete_instance"])
        self.assertFalse(instance_type.isTraceback(),
                        "Instance should not be detected as traceback")

        code_type = Type(self.test_objects["code_object"])
        self.assertFalse(code_type.isTraceback(),
                        "Code object should not be detected as traceback")

        if self.test_objects["frame_object"] is not None:
            frame_type = Type(self.test_objects["frame_object"])
            self.assertFalse(frame_type.isTraceback(),
                           "Frame object should not be detected as traceback")

        module_type = Type(self.test_objects["module_object"])
        self.assertFalse(module_type.isTraceback(),
                        "Module should not be detected as traceback")

        # Test with exception to create actual traceback
        try:
            raise ValueError("Test exception for traceback")
        except ValueError:
            import sys
            _, _, traceback_obj = sys.exc_info()
            if traceback_obj is not None:
                traceback_type = Type(traceback_obj)
                self.assertTrue(traceback_type.isTraceback(),
                               "Traceback object should be detected as traceback")