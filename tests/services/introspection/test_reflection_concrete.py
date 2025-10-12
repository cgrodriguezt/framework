import abc
import asyncio
import inspect
from typing import Any, Dict, List
from unittest.mock import Mock, patch
from orionis.test.cases.synchronous import SyncTestCase
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.services.introspection.exceptions import (
    ReflectionAttributeError,
    ReflectionTypeError,
    ReflectionValueError
)


class SimpleTestClass:
    """Simple test class for reflection testing."""

    public_attr = "public_value"
    _protected_attr = "protected_value"
    __private_attr = "private_value" # NOSONAR
    __dunder_attr__ = "dunder_value"

    def __init__(self, value: str = "default"):
        """Initialize with a value."""
        self.instance_attr = value

    def public_method(self) -> str:
        """Public method that returns a string."""
        return "public_method_result"

    def _protected_method(self) -> str:
        """Protected method that returns a string."""
        return "protected_method_result"

    def __private_method(self) -> str: # NOSONAR
        """Private method that returns a string."""
        return "private_method_result"

    async def async_method(self) -> str: # NOSONAR
        """Async method that returns a string."""
        return "async_method_result"

    @classmethod
    def class_method(cls) -> str:
        """Class method that returns a string."""
        return "class_method_result"

    @staticmethod
    def static_method() -> str:
        """Static method that returns a string."""
        return "static_method_result"

    @property
    def test_property(self) -> str:
        """Test property that returns a string."""
        return "property_value"


class AbstractTestClass(abc.ABC):
    """Abstract class for testing validation."""

    @abc.abstractmethod
    def abstract_method(self):
        """Abstract method."""
        pass


class AsyncStrTestClass:
    """Test class with async __str__ method."""

    async def __str__(self): # NOSONAR
        """Async __str__ method."""
        return "async_str"


class TestReflectionConcrete(SyncTestCase):
    """
    Comprehensive test suite for ReflectionConcrete class.

    This test class validates all functionality of the ReflectionConcrete class,
    including static validation methods, instance creation, attribute manipulation,
    method introspection, property handling, and dependency resolution.

    The tests cover both positive and negative scenarios to ensure robust
    error handling and validation across all visibility levels (public,
    protected, private, dunder) and method types (instance, class, static).
    """

    def setUp(self) -> None: # NOSONAR
        """
        Set up test environment before each test method.

        Initializes the reflection instance with SimpleTestClass and creates
        test data structures used across multiple test methods.
        """
        self.reflection = ReflectionConcrete(SimpleTestClass)
        self.test_instance = self.reflection.getInstance("test_value")

    def tearDown(self) -> None: # NOSONAR
        """
        Clean up resources after each test method completion.

        Resets reflection instances and test data to ensure clean state
        between test method executions.
        """
        self.reflection = None
        self.test_instance = None

    def testIsConcreteClassWithValidClass(self) -> None:
        """
        Test isConcreteClass method with valid concrete class.

        Validates that isConcreteClass correctly identifies valid concrete
        classes that can be used for reflection operations.

        Expected Results
        ----------------
        Returns True for valid concrete classes without raising exceptions.
        """
        result = ReflectionConcrete.isConcreteClass(SimpleTestClass)
        self.assertTrue(result)

    def testIsConcreteClassWithBuiltinType(self) -> None:
        """
        Test isConcreteClass method with built-in type.

        Validates that isConcreteClass correctly rejects built-in types
        like int, str, list as they are not suitable for reflection.

        Expected Results
        ----------------
        Returns False for built-in types without raising exceptions.
        """
        result = ReflectionConcrete.isConcreteClass(int)
        self.assertFalse(result)

        result = ReflectionConcrete.isConcreteClass(str)
        self.assertFalse(result)

        result = ReflectionConcrete.isConcreteClass(list)
        self.assertFalse(result)

    def testIsConcreteClassWithAbstractClass(self) -> None:
        """
        Test isConcreteClass method with abstract class.

        Validates that isConcreteClass correctly rejects abstract classes
        as they cannot be instantiated for reflection operations.

        Expected Results
        ----------------
        Returns False for abstract classes without raising exceptions.
        """
        result = ReflectionConcrete.isConcreteClass(AbstractTestClass)
        self.assertFalse(result)

    def testEnsureIsConcreteClassWithValidClass(self) -> None:
        """
        Test ensureIsConcreteClass method with valid concrete class.

        Validates that ensureIsConcreteClass correctly validates and accepts
        valid concrete classes suitable for reflection operations.

        Expected Results
        ----------------
        Returns True without raising exceptions for valid concrete classes.
        """
        result = ReflectionConcrete.ensureIsConcreteClass(SimpleTestClass)
        self.assertTrue(result)

    def testEnsureIsConcreteClassWithNonType(self) -> None:
        """
        Test ensureIsConcreteClass method with non-type object.

        Validates that ensureIsConcreteClass raises ReflectionTypeError
        when provided with objects that are not class types.

        Expected Results
        ----------------
        Raises ReflectionTypeError for non-type objects.
        """
        with self.assertRaises(ReflectionTypeError):
            ReflectionConcrete.ensureIsConcreteClass("not_a_class")

        with self.assertRaises(ReflectionTypeError):
            ReflectionConcrete.ensureIsConcreteClass(123)

    def testEnsureIsConcreteClassWithBuiltinType(self) -> None:
        """
        Test ensureIsConcreteClass method with built-in types.

        Validates that ensureIsConcreteClass raises ReflectionValueError
        when provided with built-in or primitive types.

        Expected Results
        ----------------
        Raises ReflectionValueError for built-in types like int, str, list.
        """
        with self.assertRaises(ReflectionValueError):
            ReflectionConcrete.ensureIsConcreteClass(int)

        with self.assertRaises(ReflectionValueError):
            ReflectionConcrete.ensureIsConcreteClass(str)

        with self.assertRaises(ReflectionValueError):
            ReflectionConcrete.ensureIsConcreteClass(list)

    def testEnsureIsConcreteClassWithAbstractClass(self) -> None:
        """
        Test ensureIsConcreteClass method with abstract class.

        Validates that ensureIsConcreteClass raises ReflectionValueError
        when provided with abstract classes that cannot be instantiated.

        Expected Results
        ----------------
        Raises ReflectionValueError for abstract classes.
        """
        with self.assertRaises(ReflectionValueError):
            ReflectionConcrete.ensureIsConcreteClass(AbstractTestClass)

    def testInitializationWithValidClass(self) -> None:
        """
        Test ReflectionConcrete initialization with valid class.

        Validates that ReflectionConcrete can be properly initialized
        with a valid concrete class and sets up internal state correctly.

        Expected Results
        ----------------
        Creates ReflectionConcrete instance without raising exceptions,
        properly initializes internal attributes.
        """
        reflection = ReflectionConcrete(SimpleTestClass)
        self.assertIsInstance(reflection, ReflectionConcrete)
        self.assertEqual(reflection.getClass(), SimpleTestClass)

    def testInitializationWithInvalidClass(self) -> None:
        """
        Test ReflectionConcrete initialization with invalid class types.

        Validates that ReflectionConcrete initialization raises appropriate
        exceptions when provided with invalid class types.

        Expected Results
        ----------------
        Raises ReflectionTypeError or ReflectionValueError for invalid types.
        """
        with self.assertRaises(ReflectionTypeError):
            ReflectionConcrete("not_a_class")

        with self.assertRaises(ReflectionValueError):
            ReflectionConcrete(int)

    def testGetInstanceWithDefaultConstructor(self) -> None:
        """
        Test getInstance method with default constructor parameters.

        Validates that getInstance can create class instances using
        default constructor parameters when available.

        Expected Results
        ----------------
        Returns valid instance of the reflected class with default values.
        """
        instance = self.reflection.getInstance()
        self.assertIsInstance(instance, SimpleTestClass)
        self.assertEqual(instance.instance_attr, "default")

    def testGetInstanceWithCustomParameters(self) -> None:
        """
        Test getInstance method with custom constructor parameters.

        Validates that getInstance can create class instances using
        custom parameters passed to the constructor.

        Expected Results
        ----------------
        Returns valid instance with custom initialization values.
        """
        instance = self.reflection.getInstance("custom_value")
        self.assertIsInstance(instance, SimpleTestClass)
        self.assertEqual(instance.instance_attr, "custom_value")

    def testGetInstanceWithAsyncStrMethod(self) -> None:
        """
        Test getInstance method with class having async __str__ method.

        Validates that getInstance raises ReflectionValueError when
        attempting to instantiate classes with async __str__ methods.

        Expected Results
        ----------------
        Raises ReflectionValueError for classes with async __str__ methods.
        """
        reflection = ReflectionConcrete(AsyncStrTestClass)
        with self.assertRaises(ReflectionValueError):
            reflection.getInstance()

    def testGetClass(self) -> None:
        """
        Test getClass method returns the reflected class type.

        Validates that getClass correctly returns the class type
        that was provided during ReflectionConcrete initialization.

        Expected Results
        ----------------
        Returns the exact class type used for reflection initialization.
        """
        result = self.reflection.getClass()
        self.assertEqual(result, SimpleTestClass)

    def testGetClassName(self) -> None:
        """
        Test getClassName method returns correct class name.

        Validates that getClassName returns the simple name of the
        reflected class without module qualification.

        Expected Results
        ----------------
        Returns string containing only the class name.
        """
        result = self.reflection.getClassName()
        self.assertEqual(result, "SimpleTestClass")

    def testGetModuleName(self) -> None:
        """
        Test getModuleName method returns correct module name.

        Validates that getModuleName returns the fully qualified
        module name where the reflected class is defined.

        Expected Results
        ----------------
        Returns string containing the full module path.
        """
        result = self.reflection.getModuleName()
        self.assertEqual(result, __name__)

    def testGetModuleWithClassName(self) -> None:
        """
        Test getModuleWithClassName method returns qualified name.

        Validates that getModuleWithClassName returns the module name
        concatenated with the class name using dot notation.

        Expected Results
        ----------------
        Returns string in format 'module.ClassName'.
        """
        result = self.reflection.getModuleWithClassName()
        expected = f"{__name__}.SimpleTestClass"
        self.assertEqual(result, expected)

    def testGetDocstring(self) -> None:
        """
        Test getDocstring method returns class docstring.

        Validates that getDocstring correctly extracts and returns
        the docstring from the reflected class definition.

        Expected Results
        ----------------
        Returns the class docstring if available, None otherwise.
        """
        result = self.reflection.getDocstring()
        self.assertEqual(result, "Simple test class for reflection testing.")

    def testGetBaseClasses(self) -> None:
        """
        Test getBaseClasses method returns inheritance hierarchy.

        Validates that getBaseClasses returns the correct list of
        base classes in the method resolution order.

        Expected Results
        ----------------
        Returns tuple containing all base classes.
        """
        result = self.reflection.getBaseClasses()
        self.assertIsInstance(result, tuple)
        self.assertIn(object, result)

    def testGetSourceCode(self) -> None:
        """
        Test getSourceCode method returns class source code.

        Validates that getSourceCode can extract and return the
        complete source code of the reflected class.

        Expected Results
        ----------------
        Returns string containing the class source code.
        """
        result = self.reflection.getSourceCode()
        self.assertIsInstance(result, str)
        self.assertIn("class SimpleTestClass", result)

    def testGetSourceCodeForMethod(self) -> None:
        """
        Test getSourceCode method for specific method.

        Validates that getSourceCode can extract source code
        for individual methods within the reflected class.

        Expected Results
        ----------------
        Returns string containing method source code.
        """
        result = self.reflection.getSourceCode("public_method")
        self.assertIsInstance(result, str)
        self.assertIn("def public_method", result)

    def testGetSourceCodeForNonExistentMethod(self) -> None:
        """
        Test getSourceCode method for non-existent method.

        Validates that getSourceCode returns None when requested
        method does not exist in the reflected class.

        Expected Results
        ----------------
        Returns None for non-existent methods.
        """
        result = self.reflection.getSourceCode("non_existent_method")
        self.assertIsNone(result)

    def testGetFile(self) -> None:
        """
        Test getFile method returns class definition file path.

        Validates that getFile correctly returns the absolute path
        to the file containing the class definition.

        Expected Results
        ----------------
        Returns string containing absolute file path.
        """
        result = self.reflection.getFile()
        self.assertIsInstance(result, str)
        self.assertTrue(result.endswith(".py"))

    def testGetAnnotations(self) -> None:
        """
        Test getAnnotations method returns type annotations.

        Validates that getAnnotations correctly extracts and processes
        type annotations defined on the reflected class.

        Expected Results
        ----------------
        Returns dictionary mapping attribute names to type annotations.
        """
        result = self.reflection.getAnnotations()
        self.assertIsInstance(result, dict)

    def testHasAttributeExisting(self) -> None:
        """
        Test hasAttribute method with existing attribute.

        Validates that hasAttribute correctly identifies when
        an attribute exists in the reflected class.

        Expected Results
        ----------------
        Returns True for existing attributes.
        """
        self.assertTrue(self.reflection.hasAttribute("public_attr"))

    def testHasAttributeNonExisting(self) -> None:
        """
        Test hasAttribute method with non-existing attribute.

        Validates that hasAttribute correctly identifies when
        an attribute does not exist in the reflected class.

        Expected Results
        ----------------
        Returns False for non-existing attributes.
        """
        self.assertFalse(self.reflection.hasAttribute("non_existent_attr"))

    def testGetAttributeExisting(self) -> None:
        """
        Test getAttribute method with existing attribute.

        Validates that getAttribute correctly retrieves the value
        of existing attributes from the reflected class.

        Expected Results
        ----------------
        Returns the actual value of the specified attribute.
        """
        result = self.reflection.getAttribute("public_attr")
        self.assertEqual(result, "public_value")

    def testGetAttributeWithDefault(self) -> None:
        """
        Test getAttribute method with default value for non-existing attribute.

        Validates that getAttribute returns the provided default value
        when the requested attribute does not exist.

        Expected Results
        ----------------
        Returns the default value for non-existing attributes.
        """
        result = self.reflection.getAttribute("non_existent", "default_val")
        self.assertEqual(result, "default_val")

    def testSetAttributeValid(self) -> None:
        """
        Test setAttribute method with valid attribute name and value.

        Validates that setAttribute can successfully add new attributes
        to the reflected class with proper validation.

        Expected Results
        ----------------
        Returns True and successfully sets the attribute value.
        """
        result = self.reflection.setAttribute("new_attr", "new_value")
        self.assertTrue(result)
        self.assertTrue(hasattr(SimpleTestClass, "new_attr"))
        self.assertEqual(getattr(SimpleTestClass, "new_attr"), "new_value")

    def testSetAttributeInvalidName(self) -> None:
        """
        Test setAttribute method with invalid attribute name.

        Validates that setAttribute raises ReflectionValueError
        when provided with invalid attribute names.

        Expected Results
        ----------------
        Raises ReflectionValueError for invalid attribute names.
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute("123invalid", "value")

        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute("class", "value")  # keyword

    def testSetAttributeCallableValue(self) -> None:
        """
        Test setAttribute method with callable value.

        Validates that setAttribute raises ReflectionValueError
        when attempting to set callable values as attributes.

        Expected Results
        ----------------
        Raises ReflectionValueError for callable values.
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute("func_attr", lambda x: x)

    def testRemoveAttributeExisting(self) -> None:
        """
        Test removeAttribute method with existing attribute.

        Validates that removeAttribute can successfully remove
        existing attributes from the reflected class.

        Expected Results
        ----------------
        Returns True and successfully removes the attribute.
        """
        # First set an attribute to remove
        self.reflection.setAttribute("temp_attr", "temp_value")
        result = self.reflection.removeAttribute("temp_attr")
        self.assertTrue(result)
        self.assertFalse(hasattr(SimpleTestClass, "temp_attr"))

    def testRemoveAttributeNonExisting(self) -> None:
        """
        Test removeAttribute method with non-existing attribute.

        Validates that removeAttribute raises ReflectionValueError
        when attempting to remove non-existing attributes.

        Expected Results
        ----------------
        Raises ReflectionValueError for non-existing attributes.
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.removeAttribute("non_existent_attr")

    def testGetAttributes(self) -> None:
        """
        Test getAttributes method returns all class attributes.

        Validates that getAttributes correctly aggregates and returns
        all attributes from different visibility levels.

        Expected Results
        ----------------
        Returns dictionary containing all class attributes.
        """
        result = self.reflection.getAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("public_attr", result)

    def testGetPublicAttributes(self) -> None:
        """
        Test getPublicAttributes method returns only public attributes.

        Validates that getPublicAttributes correctly filters and returns
        only attributes with public visibility (no underscore prefix).

        Expected Results
        ----------------
        Returns dictionary containing only public attributes.
        """
        result = self.reflection.getPublicAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("public_attr", result)
        self.assertNotIn("_protected_attr", result)

    def testGetProtectedAttributes(self) -> None:
        """
        Test getProtectedAttributes method returns only protected attributes.

        Validates that getProtectedAttributes correctly filters and returns
        only attributes with protected visibility (single underscore prefix).

        Expected Results
        ----------------
        Returns dictionary containing only protected attributes.
        """
        result = self.reflection.getProtectedAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("_protected_attr", result)

    def testGetPrivateAttributes(self) -> None:
        """
        Test getPrivateAttributes method returns only private attributes.

        Validates that getPrivateAttributes correctly filters and returns
        only attributes with private visibility (name mangling).

        Expected Results
        ----------------
        Returns dictionary containing only private attributes.
        """
        result = self.reflection.getPrivateAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("__private_attr", result)

    def testGetDunderAttributes(self) -> None:
        """
        Test getDunderAttributes method returns only dunder attributes.

        Validates that getDunderAttributes correctly filters and returns
        only attributes with dunder (magic) naming convention.

        Expected Results
        ----------------
        Returns dictionary containing only dunder attributes.
        """
        result = self.reflection.getDunderAttributes()
        self.assertIsInstance(result, dict)

    def testGetMagicAttributes(self) -> None:
        """
        Test getMagicAttributes method as alias for getDunderAttributes.

        Validates that getMagicAttributes correctly works as an alias
        for getDunderAttributes method.

        Expected Results
        ----------------
        Returns same result as getDunderAttributes method.
        """
        result = self.reflection.getMagicAttributes()
        expected = self.reflection.getDunderAttributes()
        self.assertEqual(result, expected)

    def testHasMethodExisting(self) -> None:
        """
        Test hasMethod method with existing method.

        Validates that hasMethod correctly identifies when
        a method exists in the reflected class.

        Expected Results
        ----------------
        Returns True for existing methods.
        """
        self.assertTrue(self.reflection.hasMethod("public_method"))

    def testHasMethodNonExisting(self) -> None:
        """
        Test hasMethod method with non-existing method.

        Validates that hasMethod correctly identifies when
        a method does not exist in the reflected class.

        Expected Results
        ----------------
        Returns False for non-existing methods.
        """
        self.assertFalse(self.reflection.hasMethod("non_existent_method"))

    def testCallMethodSync(self) -> None:
        """
        Test callMethod with synchronous method.

        Validates that callMethod can successfully invoke synchronous
        methods on the class instance with proper return values.

        Expected Results
        ----------------
        Returns the actual result of the method invocation.
        """
        result = self.reflection.callMethod("public_method")
        self.assertEqual(result, "public_method_result")

    def testCallMethodNonExisting(self) -> None:
        """
        Test callMethod with non-existing method.

        Validates that callMethod raises ReflectionValueError
        when attempting to call non-existing methods.

        Expected Results
        ----------------
        Raises ReflectionValueError for non-existing methods.
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.callMethod("non_existent_method")

    def testCallMethodWithoutInstance(self) -> None:
        """
        Test callMethod without initializing instance.

        Validates that callMethod raises ReflectionValueError
        when attempting to call methods without creating instance.

        Expected Results
        ----------------
        Raises ReflectionValueError when instance is not initialized.
        """
        reflection = ReflectionConcrete(SimpleTestClass)
        with self.assertRaises(ReflectionValueError):
            reflection.callMethod("public_method")

    def testSetMethodValid(self) -> None:
        """
        Test setMethod with valid method name and callable.

        Validates that setMethod can successfully add new methods
        to the reflected class with proper validation.

        Expected Results
        ----------------
        Returns True and successfully adds the method.
        """
        def new_method(self):
            return "new_method_result"

        result = self.reflection.setMethod("new_method", new_method)
        self.assertTrue(result)
        self.assertTrue(hasattr(SimpleTestClass, "new_method"))

    def testSetMethodExisting(self) -> None:
        """
        Test setMethod with existing method name.

        Validates that setMethod raises ReflectionValueError
        when attempting to set methods with existing names.

        Expected Results
        ----------------
        Raises ReflectionValueError for existing method names.
        """
        def new_method(self):
            return "result"

        with self.assertRaises(ReflectionValueError):
            self.reflection.setMethod("public_method", new_method)

    def testSetMethodInvalidName(self) -> None:
        """
        Test setMethod with invalid method name.

        Validates that setMethod raises ReflectionValueError
        when provided with invalid method names.

        Expected Results
        ----------------
        Raises ReflectionValueError for invalid method names.
        """
        def new_method(self):
            return "result"

        with self.assertRaises(ReflectionValueError):
            self.reflection.setMethod("123invalid", new_method)

    def testSetMethodNonCallable(self) -> None:
        """
        Test setMethod with non-callable value.

        Validates that setMethod raises ReflectionValueError
        when provided with non-callable values.

        Expected Results
        ----------------
        Raises ReflectionValueError for non-callable values.
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.setMethod("new_method", "not_callable")

    def testRemoveMethodExisting(self) -> None:
        """
        Test removeMethod with existing method.

        Validates that removeMethod can successfully remove
        existing methods from the reflected class.

        Expected Results
        ----------------
        Returns True and successfully removes the method.
        """
        # First add a method to remove
        def temp_method(self):
            return "temp"

        self.reflection.setMethod("temp_method", temp_method)
        
        # Clear the method cache to ensure hasMethod sees the new method
        if hasattr(self.reflection, "_ReflectionConcrete__cacheGetMethods"):
            delattr(self.reflection, "_ReflectionConcrete__cacheGetMethods")
        
        result = self.reflection.removeMethod("temp_method")
        self.assertTrue(result)
        self.assertFalse(hasattr(SimpleTestClass, "temp_method"))

    def testRemoveMethodNonExisting(self) -> None:
        """
        Test removeMethod with non-existing method.

        Validates that removeMethod raises ReflectionValueError
        when attempting to remove non-existing methods.

        Expected Results
        ----------------
        Raises ReflectionValueError for non-existing methods.
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.removeMethod("non_existent_method")

    def testGetMethodSignature(self) -> None:
        """
        Test getMethodSignature returns correct method signature.

        Validates that getMethodSignature correctly extracts and returns
        the signature information for existing methods.

        Expected Results
        ----------------
        Returns inspect.Signature object with method parameters.
        """
        result = self.reflection.getMethodSignature("public_method")
        self.assertIsInstance(result, inspect.Signature)

    def testGetMethodSignatureNonExisting(self) -> None:
        """
        Test getMethodSignature with non-existing method.

        Validates that getMethodSignature raises ReflectionValueError
        when requested method does not exist.

        Expected Results
        ----------------
        Raises ReflectionValueError for non-existing methods.
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.getMethodSignature("non_existent_method")

    def testGetMethods(self) -> None:
        """
        Test getMethods returns all method names.

        Validates that getMethods correctly aggregates and returns
        all method names from different visibility levels and types.

        Expected Results
        ----------------
        Returns list containing all method names.
        """
        result = self.reflection.getMethods()
        self.assertIsInstance(result, list)
        self.assertIn("public_method", result)

    def testGetPublicMethods(self) -> None:
        """
        Test getPublicMethods returns only public method names.

        Validates that getPublicMethods correctly filters and returns
        only methods with public visibility.

        Expected Results
        ----------------
        Returns list containing only public method names.
        """
        result = self.reflection.getPublicMethods()
        self.assertIsInstance(result, list)
        self.assertIn("public_method", result)

    def testGetPublicSyncMethods(self) -> None:
        """
        Test getPublicSyncMethods returns only synchronous public methods.

        Validates that getPublicSyncMethods correctly filters public methods
        to include only synchronous (non-coroutine) methods.

        Expected Results
        ----------------
        Returns list containing only synchronous public methods.
        """
        result = self.reflection.getPublicSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("public_method", result)
        self.assertNotIn("async_method", result)

    def testGetPublicAsyncMethods(self) -> None:
        """
        Test getPublicAsyncMethods returns only asynchronous public methods.

        Validates that getPublicAsyncMethods correctly filters public methods
        to include only asynchronous (coroutine) methods.

        Expected Results
        ----------------
        Returns list containing only asynchronous public methods.
        """
        result = self.reflection.getPublicAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("async_method", result)

    def testGetProtectedMethods(self) -> None:
        """
        Test getProtectedMethods returns only protected method names.

        Validates that getProtectedMethods correctly filters and returns
        only methods with protected visibility (single underscore).

        Expected Results
        ----------------
        Returns list containing only protected method names.
        """
        result = self.reflection.getProtectedMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protected_method", result)

    def testGetProtectedSyncMethods(self) -> None:
        """
        Test getProtectedSyncMethods returns synchronous protected methods.

        Validates that getProtectedSyncMethods correctly filters protected
        methods to include only synchronous methods.

        Expected Results
        ----------------
        Returns list containing only synchronous protected methods.
        """
        result = self.reflection.getProtectedSyncMethods()
        self.assertIsInstance(result, list)

    def testGetProtectedAsyncMethods(self) -> None:
        """
        Test getProtectedAsyncMethods returns asynchronous protected methods.

        Validates that getProtectedAsyncMethods correctly filters protected
        methods to include only asynchronous methods.

        Expected Results
        ----------------
        Returns list containing only asynchronous protected methods.
        """
        result = self.reflection.getProtectedAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateMethods(self) -> None:
        """
        Test getPrivateMethods returns only private method names.

        Validates that getPrivateMethods correctly filters and returns
        only methods with private visibility (name mangling).

        Expected Results
        ----------------
        Returns list containing only private method names.
        """
        result = self.reflection.getPrivateMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__private_method", result)

    def testGetPrivateSyncMethods(self) -> None:
        """
        Test getPrivateSyncMethods returns synchronous private methods.

        Validates that getPrivateSyncMethods correctly filters private
        methods to include only synchronous methods.

        Expected Results
        ----------------
        Returns list containing only synchronous private methods.
        """
        result = self.reflection.getPrivateSyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateAsyncMethods(self) -> None:
        """
        Test getPrivateAsyncMethods returns asynchronous private methods.

        Validates that getPrivateAsyncMethods correctly filters private
        methods to include only asynchronous methods.

        Expected Results
        ----------------
        Returns list containing only asynchronous private methods.
        """
        result = self.reflection.getPrivateAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPublicClassMethods(self) -> None:
        """
        Test getPublicClassMethods returns only public class methods.

        Validates that getPublicClassMethods correctly filters and returns
        only class methods with public visibility.

        Expected Results
        ----------------
        Returns list containing only public class method names.
        """
        result = self.reflection.getPublicClassMethods()
        self.assertIsInstance(result, list)
        self.assertIn("class_method", result)

    def testGetPublicClassSyncMethods(self) -> None:
        """
        Test getPublicClassSyncMethods returns synchronous public class methods.

        Validates that getPublicClassSyncMethods correctly filters public
        class methods to include only synchronous methods.

        Expected Results
        ----------------
        Returns list containing only synchronous public class methods.
        """
        result = self.reflection.getPublicClassSyncMethods()
        self.assertIsInstance(result, list)

    def testGetPublicClassAsyncMethods(self) -> None:
        """
        Test getPublicClassAsyncMethods returns asynchronous public class methods.

        Validates that getPublicClassAsyncMethods correctly filters public
        class methods to include only asynchronous methods.

        Expected Results
        ----------------
        Returns list containing only asynchronous public class methods.
        """
        result = self.reflection.getPublicClassAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPublicStaticMethods(self) -> None:
        """
        Test getPublicStaticMethods returns only public static methods.

        Validates that getPublicStaticMethods correctly filters and returns
        only static methods with public visibility.

        Expected Results
        ----------------
        Returns list containing only public static method names.
        """
        result = self.reflection.getPublicStaticMethods()
        self.assertIsInstance(result, list)
        self.assertIn("static_method", result)

    def testGetPublicStaticSyncMethods(self) -> None:
        """
        Test getPublicStaticSyncMethods returns synchronous public static methods.

        Validates that getPublicStaticSyncMethods correctly filters public
        static methods to include only synchronous methods.

        Expected Results
        ----------------
        Returns list containing only synchronous public static methods.
        """
        result = self.reflection.getPublicStaticSyncMethods()
        self.assertIsInstance(result, list)

    def testGetPublicStaticAsyncMethods(self) -> None:
        """
        Test getPublicStaticAsyncMethods returns asynchronous public static methods.

        Validates that getPublicStaticAsyncMethods correctly filters public
        static methods to include only asynchronous methods.

        Expected Results
        ----------------
        Returns list containing only asynchronous public static methods.
        """
        result = self.reflection.getPublicStaticAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetDunderMethods(self) -> None:
        """
        Test getDunderMethods returns only dunder method names.

        Validates that getDunderMethods correctly filters and returns
        only methods with dunder (magic) naming convention.

        Expected Results
        ----------------
        Returns list containing only dunder method names.
        """
        result = self.reflection.getDunderMethods()
        self.assertIsInstance(result, list)

    def testGetMagicMethods(self) -> None:
        """
        Test getMagicMethods as alias for getDunderMethods.

        Validates that getMagicMethods correctly works as an alias
        for getDunderMethods method.

        Expected Results
        ----------------
        Returns same result as getDunderMethods method.
        """
        result = self.reflection.getMagicMethods()
        expected = self.reflection.getDunderMethods()
        self.assertEqual(result, expected)

    def testGetProperties(self) -> None:
        """
        Test getProperties returns all property names.

        Validates that getProperties correctly identifies and returns
        all properties defined in the reflected class.

        Expected Results
        ----------------
        Returns list containing all property names.
        """
        result = self.reflection.getProperties()
        self.assertIsInstance(result, list)
        self.assertIn("test_property", result)

    def testGetPublicProperties(self) -> None:
        """
        Test getPublicProperties returns only public properties.

        Validates that getPublicProperties correctly filters and returns
        only properties with public visibility.

        Expected Results
        ----------------
        Returns list containing only public property names.
        """
        result = self.reflection.getPublicProperties()
        self.assertIsInstance(result, list)
        self.assertIn("test_property", result)

    def testGetProtectedProperties(self) -> None:
        """
        Test getProtectedProperties returns only protected properties.

        Validates that getProtectedProperties correctly filters and returns
        only properties with protected visibility.

        Expected Results
        ----------------
        Returns list containing only protected property names.
        """
        result = self.reflection.getProtectedProperties()
        self.assertIsInstance(result, list)

    def testGetPrivateProperties(self) -> None:
        """
        Test getPrivateProperties returns only private properties.

        Validates that getPrivateProperties correctly filters and returns
        only properties with private visibility.

        Expected Results
        ----------------
        Returns list containing only private property names.
        """
        result = self.reflection.getPrivateProperties()
        self.assertIsInstance(result, list)

    def testGetConstructorSignature(self) -> None:
        """
        Test getConstructorSignature returns constructor signature.

        Validates that getConstructorSignature correctly extracts and returns
        the signature information for the class constructor.

        Expected Results
        ----------------
        Returns inspect.Signature object with constructor parameters.
        """
        result = self.reflection.getConstructorSignature()
        self.assertIsInstance(result, inspect.Signature)

    def testGetConstructorDependencies(self) -> None:
        """
        Test getConstructorDependencies returns dependency analysis.

        Validates that getConstructorDependencies correctly analyzes
        constructor parameters and returns dependency information.

        Expected Results
        ----------------
        Returns ResolveArguments object with dependency analysis.
        """
        result = self.reflection.getConstructorDependencies()
        self.assertIsNotNone(result)

    def testGetMethodDependencies(self) -> None:
        """
        Test getMethodDependencies returns method dependency analysis.

        Validates that getMethodDependencies correctly analyzes method
        parameters and returns dependency information.

        Expected Results
        ----------------
        Returns ResolveArguments object with method dependency analysis.
        """
        result = self.reflection.getMethodDependencies("public_method")
        self.assertIsNotNone(result)

    def testGetMethodDependenciesNonExisting(self) -> None:
        """
        Test getMethodDependencies with non-existing method.

        Validates that getMethodDependencies raises ReflectionAttributeError
        when requested method does not exist.

        Expected Results
        ----------------
        Raises ReflectionAttributeError for non-existing methods.
        """
        with self.assertRaises(ReflectionAttributeError):
            self.reflection.getMethodDependencies("non_existent_method")

    def testReflectionInstanceWithoutInstance(self) -> None:
        """
        Test reflectionInstance without creating instance first.

        Validates that reflectionInstance raises ReflectionValueError
        when attempting to get instance reflection without initialization.

        Expected Results
        ----------------
        Raises ReflectionValueError when instance is not initialized.
        """
        reflection = ReflectionConcrete(SimpleTestClass)
        with self.assertRaises(ReflectionValueError):
            reflection.reflectionInstance()

    def testReflectionInstanceWithInstance(self) -> None:
        """
        Test reflectionInstance with properly created instance.

        Validates that reflectionInstance returns proper ReflectionInstance
        object when class instance has been created.

        Expected Results
        ----------------
        Returns ReflectionInstance object for instance-level operations.
        """
        result = self.reflection.reflectionInstance()
        self.assertIsNotNone(result)

    def testPrivateAttributeNameMangling(self) -> None:
        """
        Test private attribute name mangling handling.

        Validates that the reflection system correctly handles Python's
        name mangling for private attributes with double underscore prefix.

        Expected Results
        ----------------
        Correctly processes private attributes with name mangling.
        """
        self.reflection.setAttribute("__test_private", "private_val")
        self.assertTrue(hasattr(SimpleTestClass, "_SimpleTestClass__test_private"))

    def testPrivateMethodNameMangling(self) -> None:
        """
        Test private method name mangling handling.

        Validates that the reflection system correctly handles Python's
        name mangling for private methods with double underscore prefix.

        Expected Results
        ----------------
        Correctly processes private methods with name mangling.
        """
        def private_method(self):
            return "private_result"

        self.reflection.setMethod("__test_private_method", private_method)
        self.assertTrue(hasattr(SimpleTestClass, "_SimpleTestClass__test_private_method"))

    def testCacheInvalidationAfterAttributeModification(self) -> None:
        """
        Test cache invalidation after attribute modifications.

        Validates that internal caches are properly invalidated when
        class attributes are modified to ensure data consistency.

        Expected Results
        ----------------
        Cache is invalidated and refreshed after modifications.
        """

        # Add new attribute
        self.reflection.setAttribute("cache_test_attr", "test_value")

        # Clear cache manually to test invalidation
        if hasattr(self.reflection, "_ReflectionConcrete__cacheGetAttributes"):
            delattr(self.reflection, "_ReflectionConcrete__cacheGetAttributes")

        # Get attributes again - should include new attribute
        updated_attrs = self.reflection.getAttributes()
        self.assertIn("cache_test_attr", updated_attrs)

    def testEdgeCaseWithDynamicallyCreatedClass(self) -> None:
        """
        Test reflection with dynamically created class.

        Validates that ReflectionConcrete can handle classes created
        dynamically at runtime using type() function.

        Expected Results
        ----------------
        Successfully creates reflection for dynamic classes.
        """
        # Create a dynamic class
        DynamicClass = type('DynamicClass', (object,), {
            'dynamic_attr': 'dynamic_value',
            'dynamic_method': lambda self: 'dynamic_result'
        })

        # Test reflection with dynamic class
        dynamic_reflection = ReflectionConcrete(DynamicClass)
        self.assertEqual(dynamic_reflection.getClassName(), "DynamicClass")
        self.assertTrue(dynamic_reflection.hasAttribute("dynamic_attr"))
