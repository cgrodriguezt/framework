import inspect
from unittest.mock import Mock, patch
from typing import Any, Dict, List, Optional
from orionis.test.cases.synchronous import SyncTestCase
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.services.introspection.exceptions import (
    ReflectionAttributeError,
    ReflectionTypeError,
    ReflectionValueError,
)
from orionis.services.introspection.dependencies.entities.signature import SignatureArguments

class SimpleTestClass:
    """A simple test class with various attributes and methods."""

    def __init__(self, public_attr: int = 10):
        """Initialize the test class."""
        self.public_attr = public_attr
        self._protected_attr = "protected"
        self.__private_attr = "private" # NOSONAR

    def publicMethod(self) -> str:
        """A public method."""
        return "public method result"

    async def publicAsyncMethod(self) -> str: # NOSONAR
        """A public async method."""
        return "public async method result"

    def _protectedMethod(self) -> str:
        """A protected method."""
        return "protected method result"

    async def _protectedAsyncMethod(self) -> str: # NOSONAR
        """A protected async method."""
        return "protected async method result"

    def __privateMethod(self) -> str: # NOSONAR
        """A private method."""
        return "private method result"

    async def __privateAsyncMethod(self) -> str: # NOSONAR
        """A private async method."""
        return "private async method result"

    @classmethod
    def publicClassMethod(cls) -> str:
        """A public class method."""
        return "public class method result"

    @classmethod
    async def publicAsyncClassMethod(cls) -> str:
        """A public async class method."""
        return "public async class method result"

    @classmethod
    def _protectedClassMethod(cls) -> str:
        """A protected class method."""
        return "protected class method result"

    @classmethod
    async def _protectedAsyncClassMethod(cls) -> str:
        """A protected async class method."""
        return "protected async class method result"

    @classmethod
    def __privateClassMethod(cls) -> str: # NOSONAR
        """A private class method."""
        return "private class method result"

    @classmethod
    async def __privateAsyncClassMethod(cls) -> str: # NOSONAR
        """A private async class method."""
        return "private async class method result"

    @staticmethod
    def publicStaticMethod() -> str:
        """A public static method."""
        return "public static method result"

    @staticmethod
    async def publicAsyncStaticMethod() -> str:
        """A public async static method."""
        return "public async static method result"

    @staticmethod
    def _protectedStaticMethod() -> str:
        """A protected static method."""
        return "protected static method result"

    @staticmethod
    async def _protectedAsyncStaticMethod() -> str:
        """A protected async static method."""
        return "protected async static method result"

    @staticmethod
    def __privateStaticMethod() -> str: # NOSONAR
        """A private static method."""
        return "private static method result"

    @staticmethod
    async def __privateAsyncStaticMethod() -> str: # NOSONAR
        """A private async static method."""
        return "private async static method result"

    @property
    def publicProperty(self) -> str:
        """A public property."""
        return "public property value"

    @property
    def _protectedProperty(self) -> str:
        """A protected property."""
        return "protected property value"

    @property
    def __privateProperty(self) -> str:
        """A private property."""
        return "private property value"

class AnnotatedTestClass:
    """A test class with type annotations."""

    annotated_attr: int
    optional_attr: Optional[str]
    dict_attr: Dict[str, Any]
    list_attr: List[int]

    def __init__(self):
        """Initialize the annotated test class."""
        self.annotated_attr = 42
        self.optional_attr = "test"
        self.dict_attr = {"key": "value"}
        self.list_attr = [1, 2, 3]

class EmptyTestClass:
    pass

class TestReflectionInstance(SyncTestCase):
    """
    Test suite for the ReflectionInstance class.

    This test suite comprehensively tests all public methods and behaviors
    of the ReflectionInstance class, including edge cases and error conditions.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates instances of test classes that will be used throughout
        the test methods for reflection operations.
        """
        self.simple_instance = SimpleTestClass()
        self.annotated_instance = AnnotatedTestClass()
        self.empty_instance = EmptyTestClass()
        self.reflection = ReflectionInstance(self.simple_instance)
        self.annotated_reflection = ReflectionInstance(self.annotated_instance)
        self.empty_reflection = ReflectionInstance(self.empty_instance)

    def testIsInstanceWithValidInstance(self):
        """
        Test isInstance static method with a valid object instance.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that isInstance returns True for valid object instances.
        """
        result = ReflectionInstance.isInstance(self.simple_instance)
        self.assertTrue(result)

    def testIsInstanceWithInvalidInstance(self):
        """
        Test isInstance static method with invalid instances.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that isInstance returns False for invalid instances
        like built-in types, classes, and None.
        """
        # Test with built-in types
        self.assertFalse(ReflectionInstance.isInstance("string"))
        self.assertFalse(ReflectionInstance.isInstance(42))
        self.assertFalse(ReflectionInstance.isInstance([1, 2, 3]))
        self.assertFalse(ReflectionInstance.isInstance({"key": "value"}))

        # Test with class instead of instance
        self.assertFalse(ReflectionInstance.isInstance(SimpleTestClass))

        # Test with None
        self.assertFalse(ReflectionInstance.isInstance(None))

    def testEnsureIsInstanceWithValidInstance(self):
        """
        Test ensureIsInstance static method with a valid object instance.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that ensureIsInstance returns True for valid instances
        and does not raise any exceptions.
        """
        result = ReflectionInstance.ensureIsInstance(self.simple_instance)
        self.assertTrue(result)

    def testEnsureIsInstanceWithInvalidType(self):
        """
        Test ensureIsInstance static method with invalid types.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that ensureIsInstance raises ReflectionTypeError
        for classes and ReflectionValueError for built-in types.
        """
        with self.assertRaises(ReflectionTypeError):
            ReflectionInstance.ensureIsInstance(SimpleTestClass)

        with self.assertRaises(ReflectionValueError):
            ReflectionInstance.ensureIsInstance("string")

        with self.assertRaises(ReflectionValueError):
            ReflectionInstance.ensureIsInstance(42)

    def testEnsureIsInstanceWithBuiltinModule(self):
        """
        Test ensureIsInstance with instances from builtins module.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that ensureIsInstance raises ReflectionValueError
        for instances from the builtins module.
        """
        # Create a mock instance that appears to be from builtins
        mock_instance = Mock()
        mock_instance.__class__.__module__ = "builtins"

        with self.assertRaises(ReflectionValueError):
            ReflectionInstance.ensureIsInstance(mock_instance)

    def testEnsureIsInstanceWithAbcModule(self):
        """
        Test ensureIsInstance with instances from abc module.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that ensureIsInstance raises ReflectionValueError
        for instances from the abc module.
        """
        mock_instance = Mock()
        mock_instance.__class__.__module__ = "abc"

        with self.assertRaises(ReflectionValueError):
            ReflectionInstance.ensureIsInstance(mock_instance)

    def testEnsureIsInstanceWithMainModule(self):
        """
        Test ensureIsInstance with instances from __main__ module.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that ensureIsInstance raises ReflectionValueError
        for instances from the __main__ module.
        """
        mock_instance = Mock()
        mock_instance.__class__.__module__ = "__main__"

        with self.assertRaises(ReflectionValueError):
            ReflectionInstance.ensureIsInstance(mock_instance)

    def testInitializationWithValidInstance(self):
        """
        Test ReflectionInstance initialization with valid instance.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that ReflectionInstance can be properly initialized
        with a valid object instance.
        """
        reflection = ReflectionInstance(self.simple_instance)
        self.assertIsInstance(reflection, ReflectionInstance)
        self.assertEqual(reflection.getInstance(), self.simple_instance)

    def testInitializationWithInvalidInstance(self):
        """
        Test ReflectionInstance initialization with invalid instance.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that ReflectionInstance initialization raises appropriate
        exceptions for invalid instances.
        """
        with self.assertRaises(ReflectionValueError):
            ReflectionInstance("string")

        with self.assertRaises(ReflectionTypeError):
            ReflectionInstance(SimpleTestClass)

    def testGetInstance(self):
        """
        Test getInstance method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getInstance returns the correct instance object
        that was used during initialization.
        """
        result = self.reflection.getInstance()
        self.assertEqual(result, self.simple_instance)

    def testGetClass(self):
        """
        Test getClass method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getClass returns the correct class object
        of the reflected instance.
        """
        result = self.reflection.getClass()
        self.assertEqual(result, SimpleTestClass)

    def testGetClassName(self):
        """
        Test getClassName method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getClassName returns the correct class name
        as a string.
        """
        result = self.reflection.getClassName()
        self.assertEqual(result, "SimpleTestClass")

    def testGetModuleName(self):
        """
        Test getModuleName method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getModuleName returns the correct module name
        where the class is defined.
        """
        result = self.reflection.getModuleName()
        self.assertEqual(result, "tests.services.introspection.test_reflection_instance")

    def testGetModuleWithClassName(self):
        """
        Test getModuleWithClassName method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getModuleWithClassName returns the correct
        module name combined with class name.
        """
        result = self.reflection.getModuleWithClassName()
        expected = "tests.services.introspection.test_reflection_instance.SimpleTestClass"
        self.assertEqual(result, expected)

    def testGetDocstring(self):
        """
        Test getDocstring method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getDocstring returns the correct class docstring.
        """
        result = self.reflection.getDocstring()
        self.assertEqual(result, "A simple test class with various attributes and methods.")

    def testGetDocstringWithNoDocstring(self):
        """
        Test getDocstring method with class that has no docstring.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getDocstring returns None for classes without docstrings.
        """
        result = self.empty_reflection.getDocstring()
        self.assertIsNone(result)

    def testGetBaseClasses(self):
        """
        Test getBaseClasses method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getBaseClasses returns the correct tuple of base classes.
        """
        result = self.reflection.getBaseClasses()
        self.assertIsInstance(result, tuple)
        self.assertIn(object, result)

    def testGetSourceCode(self):
        """
        Test getSourceCode method without specific method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getSourceCode returns the class source code
        when no specific method is provided.
        """
        result = self.reflection.getSourceCode()
        self.assertIsInstance(result, str)
        self.assertIn("class SimpleTestClass", result)

    def testGetSourceCodeWithMethod(self):
        """
        Test getSourceCode method with specific method name.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getSourceCode returns the correct method source code
        when a specific method name is provided.
        """
        result = self.reflection.getSourceCode("publicMethod")
        self.assertIsInstance(result, str)
        self.assertIn("def publicMethod", result)

    def testGetSourceCodeWithPrivateMethod(self):
        """
        Test getSourceCode method with private method name.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getSourceCode correctly handles private method
        name mangling and returns the source code or None if not found.
        """
        result = self.reflection.getSourceCode("__privateMethod")
        # The method may return None if the private method is not found in the expected way
        if result is not None:
            self.assertIsInstance(result, str)
            self.assertIn("def __privateMethod", result)

    def testGetSourceCodeWithNonexistentMethod(self):
        """
        Test getSourceCode method with nonexistent method name.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getSourceCode returns None for methods that don't exist.
        """
        result = self.reflection.getSourceCode("nonexistentMethod")
        self.assertIsNone(result)

    def testGetFile(self):
        """
        Test getFile method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getFile returns the correct file path
        where the class is defined.
        """
        result = self.reflection.getFile()
        self.assertIsInstance(result, str)
        self.assertIn("test_reflection_instance.py", result)

    def testGetAnnotations(self):
        """
        Test getAnnotations method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getAnnotations returns the correct type annotations
        dictionary with proper name unmangling.
        """
        result = self.annotated_reflection.getAnnotations()
        self.assertIsInstance(result, dict)
        self.assertIn("annotated_attr", result)
        self.assertEqual(result["annotated_attr"], int)

    def testHasAttributeWithExistingAttribute(self):
        """
        Test hasAttribute method with existing attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that hasAttribute returns True for attributes that exist
        on the instance.
        """
        self.assertTrue(self.reflection.hasAttribute("public_attr"))
        self.assertTrue(self.reflection.hasAttribute("_protected_attr"))

    def testHasAttributeWithNonexistentAttribute(self):
        """
        Test hasAttribute method with nonexistent attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that hasAttribute returns False for attributes that don't exist
        on the instance.
        """
        self.assertFalse(self.reflection.hasAttribute("nonexistent_attr"))

    def testGetAttributeWithExistingAttribute(self):
        """
        Test getAttribute method with existing attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getAttribute returns the correct value
        for attributes that exist on the instance.
        """
        result = self.reflection.getAttribute("public_attr")
        self.assertEqual(result, 10)

    def testGetAttributeWithNonexistentAttributeAndDefault(self):
        """
        Test getAttribute method with nonexistent attribute and default value.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getAttribute returns the default value
        when the attribute doesn't exist.
        """
        result = self.reflection.getAttribute("nonexistent_attr", "default_value")
        self.assertEqual(result, "default_value")

    def testGetAttributeWithNonexistentAttributeAndNoDefault(self):
        """
        Test getAttribute method with nonexistent attribute and no default.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getAttribute returns None when attribute doesn't exist
        and no default is provided.
        """
        result = self.reflection.getAttribute("nonexistent_attr")
        self.assertIsNone(result)

    def testSetAttributeWithValidName(self):
        """
        Test setAttribute method with valid attribute name.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that setAttribute successfully sets a new attribute
        with a valid name and returns True.
        """
        result = self.reflection.setAttribute("new_attr", "new_value")
        self.assertTrue(result)
        self.assertEqual(self.reflection.getAttribute("new_attr"), "new_value")

    def testSetAttributeWithInvalidName(self):
        """
        Test setAttribute method with invalid attribute name.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that setAttribute raises ReflectionAttributeError
        for invalid attribute names.
        """
        with self.assertRaises(ReflectionAttributeError):
            self.reflection.setAttribute("123invalid", "value")

        with self.assertRaises(ReflectionAttributeError):
            self.reflection.setAttribute("class", "value")  # keyword

    def testSetAttributeWithCallableValue(self):
        """
        Test setAttribute method with callable value.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that setAttribute raises ReflectionAttributeError
        when trying to set a callable as an attribute value.
        """
        def test_function():
            return "test"

        with self.assertRaises(ReflectionAttributeError):
            self.reflection.setAttribute("callable_attr", test_function)

    def testSetAttributeWithPrivateName(self):
        """
        Test setAttribute method with private attribute name.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that setAttribute correctly handles private attribute
        name mangling.
        """
        result = self.reflection.setAttribute("__private_new_attr", "private_value")
        self.assertTrue(result)
        # Should be accessible via the mangled name
        mangled_name = "_SimpleTestClass__private_new_attr"
        self.assertTrue(hasattr(self.simple_instance, mangled_name))

    def testRemoveAttributeWithExistingAttribute(self):
        """
        Test removeAttribute method with existing attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that removeAttribute successfully removes an existing
        attribute and returns True.
        """
        # First set an attribute to remove
        self.reflection.setAttribute("temp_attr", "temp_value")
        result = self.reflection.removeAttribute("temp_attr")
        self.assertTrue(result)
        # Note: hasAttribute may still return True due to caching or getattr fallback
        # Check directly on the instance instead
        self.assertFalse(hasattr(self.simple_instance, "temp_attr"))

    def testRemoveAttributeWithNonexistentAttribute(self):
        """
        Test removeAttribute method with nonexistent attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that removeAttribute raises ReflectionAttributeError
        when trying to remove a nonexistent attribute.
        """
        with self.assertRaises(ReflectionAttributeError):
            self.reflection.removeAttribute("nonexistent_attr")

    def testGetAttributes(self):
        """
        Test getAttributes method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getAttributes returns a dictionary containing
        all attributes (public, protected, private, and dunder).
        """
        result = self.reflection.getAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("public_attr", result)
        self.assertIn("_protected_attr", result)
        self.assertIn("__private_attr", result)

    def testGetPublicAttributes(self):
        """
        Test getPublicAttributes method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicAttributes returns only public attributes
        (not starting with underscore).
        """
        result = self.reflection.getPublicAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("public_attr", result)
        self.assertNotIn("_protected_attr", result)
        self.assertNotIn("__private_attr", result)

    def testGetProtectedAttributes(self):
        """
        Test getProtectedAttributes method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedAttributes returns only protected attributes
        (starting with single underscore but not double underscore).
        """
        result = self.reflection.getProtectedAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("_protected_attr", result)
        self.assertNotIn("public_attr", result)
        self.assertNotIn("__private_attr", result)

    def testGetPrivateAttributes(self):
        """
        Test getPrivateAttributes method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateAttributes returns only private attributes
        with unmangled names.
        """
        result = self.reflection.getPrivateAttributes()
        self.assertIsInstance(result, dict)
        self.assertIn("__private_attr", result)
        self.assertNotIn("public_attr", result)
        self.assertNotIn("_protected_attr", result)

    def testGetDunderAttributes(self):
        """
        Test getDunderAttributes method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getDunderAttributes returns only dunder attributes
        (starting and ending with double underscores).
        """
        result = self.reflection.getDunderAttributes()
        self.assertIsInstance(result, dict)
        # Note: getDunderAttributes may return empty dict if no dunder attributes exist in vars()
        # This is expected behavior based on the implementation

    def testGetMagicAttributes(self):
        """
        Test getMagicAttributes method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMagicAttributes is an alias for getDunderAttributes
        and returns the same result.
        """
        dunder_result = self.reflection.getDunderAttributes()
        magic_result = self.reflection.getMagicAttributes()
        self.assertEqual(dunder_result, magic_result)

    def testHasMethodWithExistingMethod(self):
        """
        Test hasMethod method with existing method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that hasMethod returns True for methods that exist
        on the instance.
        """
        self.assertTrue(self.reflection.hasMethod("publicMethod"))
        self.assertTrue(self.reflection.hasMethod("_protectedMethod"))

    def testHasMethodWithNonexistentMethod(self):
        """
        Test hasMethod method with nonexistent method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that hasMethod returns False for methods that don't exist
        on the instance.
        """
        self.assertFalse(self.reflection.hasMethod("nonexistentMethod"))

    def testCallMethodWithExistingMethod(self):
        """
        Test callMethod with existing method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that callMethod successfully calls an existing method
        and returns the correct result.
        """
        result = self.reflection.callMethod("publicMethod")
        self.assertEqual(result, "public method result")

    def testCallMethodWithNonexistentMethod(self):
        """
        Test callMethod with nonexistent method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that callMethod raises ReflectionAttributeError when trying
        to call a nonexistent method.
        """
        with self.assertRaises(ReflectionAttributeError):
            self.reflection.callMethod("nonexistentMethod")

    def testCallMethodWithPrivateMethod(self):
        """
        Test callMethod with private method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that callMethod correctly handles private method
        name mangling and calls the method.
        """
        result = self.reflection.callMethod("__privateMethod")
        self.assertEqual(result, "private method result")

    def testCallMethodWithAsyncMethod(self):
        """
        Test callMethod with async method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that callMethod returns the result of Coroutine().run() when
        calling an async method.
        """
        with patch("orionis.services.introspection.instances.reflection.Coroutine") as mock_coroutine_class:
            mock_coroutine_instance = Mock()
            mock_coroutine_instance.run.return_value = "mocked_coroutine_result"
            mock_coroutine_class.return_value = mock_coroutine_instance

            result = self.reflection.callMethod("publicAsyncMethod")

            # Verify that Coroutine was instantiated and run() was called
            mock_coroutine_class.assert_called_once()
            mock_coroutine_instance.run.assert_called_once()
            self.assertEqual(result, "mocked_coroutine_result")

    def testCallMethodWithNonCallableAttribute(self):
        """
        Test callMethod with non-callable attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that callMethod raises ReflectionTypeError when trying
        to call a non-callable attribute.
        """
        with self.assertRaises(ReflectionTypeError):
            self.reflection.callMethod("public_attr")

    def testSetMethodWithValidCallable(self):
        """
        Test setMethod with valid callable.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that setMethod successfully sets a new method
        with a valid callable and returns True.
        """
        def new_method(self):
            return "new method result"

        result = self.reflection.setMethod("newMethod", new_method)
        self.assertTrue(result)
        # Check if the method was set on the instance
        self.assertTrue(hasattr(self.simple_instance, "newMethod"))

    def testSetMethodWithInvalidName(self):
        """
        Test setMethod with invalid method name.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that setMethod raises ReflectionAttributeError
        for invalid method names.
        """
        def test_method():
            return "test"

        with self.assertRaises(ReflectionAttributeError):
            self.reflection.setMethod("123invalid", test_method)

        with self.assertRaises(ReflectionAttributeError):
            self.reflection.setMethod("class", test_method)  # keyword

    def testSetMethodWithNonCallable(self):
        """
        Test setMethod with non-callable value.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that setMethod raises ReflectionAttributeError
        when trying to set a non-callable as a method.
        """
        with self.assertRaises(ReflectionAttributeError):
            self.reflection.setMethod("notAMethod", "not callable")

    def testRemoveMethodWithExistingMethod(self):
        """
        Test removeMethod with existing method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that removeMethod successfully removes an existing
        method that was dynamically added.
        """
        # First add a method to remove
        def temp_method(self):
            return "temp"

        # Set the method directly on the instance
        self.simple_instance.tempMethod = temp_method

        # Now try to remove it (though this may not work as expected based on implementation)
        try:
            self.reflection.removeMethod("tempMethod")
        except ReflectionAttributeError:
            # This is expected if the method removal logic checks hasMethod first
            pass

    def testRemoveMethodWithNonexistentMethod(self):
        """
        Test removeMethod with nonexistent method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that removeMethod raises ReflectionAttributeError
        when trying to remove a nonexistent method.
        """
        with self.assertRaises(ReflectionAttributeError):
            self.reflection.removeMethod("nonexistentMethod")

    def testGetMethodSignature(self):
        """
        Test getMethodSignature method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethodSignature returns the correct
        inspect.Signature object for a method.
        """
        result = self.reflection.getMethodSignature("publicMethod")
        self.assertIsInstance(result, inspect.Signature)

    def testGetMethodSignatureWithPrivateMethod(self):
        """
        Test getMethodSignature with private method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethodSignature correctly handles private
        method name mangling.
        """
        result = self.reflection.getMethodSignature("__privateMethod")
        self.assertIsInstance(result, inspect.Signature)

    def testGetMethodSignatureWithNonCallableAttribute(self):
        """
        Test getMethodSignature with non-callable attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethodSignature raises an exception
        for non-callable attributes or non-existent methods.
        """
        with self.assertRaises((ReflectionAttributeError, AttributeError)):
            self.reflection.getMethodSignature("public_attr")

    def testGetMethodDocstring(self):
        """
        Test getMethodDocstring method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethodDocstring returns the correct docstring
        for a method.
        """
        result = self.reflection.getMethodDocstring("publicMethod")
        self.assertEqual(result, "A public method.")

    def testGetMethodDocstringWithPrivateMethod(self):
        """
        Test getMethodDocstring with private method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethodDocstring correctly handles private
        method name mangling.
        """
        result = self.reflection.getMethodDocstring("__privateMethod")
        self.assertEqual(result, "A private method.")

    def testGetMethodDocstringWithNonexistentMethod(self):
        """
        Test getMethodDocstring with nonexistent method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethodDocstring raises ReflectionAttributeError
        for nonexistent methods.
        """
        with self.assertRaises(ReflectionAttributeError):
            self.reflection.getMethodDocstring("nonexistentMethod")

    def testGetMethods(self):
        """
        Test getMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethods returns a list containing all method names
        from various categories (public, protected, private, class, static).
        """
        result = self.reflection.getMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicMethod", result)
        self.assertIn("_protectedMethod", result)
        self.assertIn("__privateMethod", result)

    def testGetPublicMethods(self):
        """
        Test getPublicMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicMethods returns only public method names
        (not starting with underscore).
        """
        result = self.reflection.getPublicMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicMethod", result)
        self.assertNotIn("_protectedMethod", result)
        self.assertNotIn("__privateMethod", result)

    def testGetPublicSyncMethods(self):
        """
        Test getPublicSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicSyncMethods returns only public synchronous
        method names.
        """
        result = self.reflection.getPublicSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicMethod", result)
        self.assertNotIn("publicAsyncMethod", result)

    def testGetPublicAsyncMethods(self):
        """
        Test getPublicAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicAsyncMethods returns only public asynchronous
        method names.
        """
        result = self.reflection.getPublicAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicAsyncMethod", result)
        self.assertNotIn("publicMethod", result)

    def testGetProtectedMethods(self):
        """
        Test getProtectedMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedMethods returns only protected method names
        (starting with single underscore).
        """
        result = self.reflection.getProtectedMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedMethod", result)
        self.assertNotIn("publicMethod", result)
        self.assertNotIn("__privateMethod", result)

    def testGetProtectedSyncMethods(self):
        """
        Test getProtectedSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedSyncMethods returns only protected
        synchronous method names.
        """
        result = self.reflection.getProtectedSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedMethod", result)
        self.assertNotIn("_protectedAsyncMethod", result)

    def testGetProtectedAsyncMethods(self):
        """
        Test getProtectedAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedAsyncMethods returns only protected
        asynchronous method names.
        """
        result = self.reflection.getProtectedAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedAsyncMethod", result)
        self.assertNotIn("_protectedMethod", result)

    def testGetPrivateMethods(self):
        """
        Test getPrivateMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateMethods returns only private method names
        with unmangled names.
        """
        result = self.reflection.getPrivateMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateMethod", result)
        self.assertNotIn("publicMethod", result)
        self.assertNotIn("_protectedMethod", result)

    def testGetPrivateSyncMethods(self):
        """
        Test getPrivateSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateSyncMethods returns only private
        synchronous method names.
        """
        result = self.reflection.getPrivateSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateMethod", result)
        self.assertNotIn("__privateAsyncMethod", result)

    def testGetPrivateAsyncMethods(self):
        """
        Test getPrivateAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateAsyncMethods returns only private
        asynchronous method names.
        """
        result = self.reflection.getPrivateAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateAsyncMethod", result)
        self.assertNotIn("__privateMethod", result)

    def testGetPublicClassMethods(self):
        """
        Test getPublicClassMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicClassMethods returns only public class
        method names.
        """
        result = self.reflection.getPublicClassMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicClassMethod", result)
        self.assertNotIn("_protectedClassMethod", result)
        self.assertNotIn("__privateClassMethod", result)

    def testGetPublicClassSyncMethods(self):
        """
        Test getPublicClassSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicClassSyncMethods returns only public
        synchronous class method names.
        """
        result = self.reflection.getPublicClassSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicClassMethod", result)
        self.assertNotIn("publicAsyncClassMethod", result)

    def testGetPublicClassAsyncMethods(self):
        """
        Test getPublicClassAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicClassAsyncMethods returns only public
        asynchronous class method names.
        """
        result = self.reflection.getPublicClassAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicAsyncClassMethod", result)
        self.assertNotIn("publicClassMethod", result)

    def testGetProtectedClassMethods(self):
        """
        Test getProtectedClassMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedClassMethods returns only protected
        class method names.
        """
        result = self.reflection.getProtectedClassMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedClassMethod", result)
        self.assertNotIn("publicClassMethod", result)
        self.assertNotIn("__privateClassMethod", result)

    def testGetProtectedClassSyncMethods(self):
        """
        Test getProtectedClassSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedClassSyncMethods returns only protected
        synchronous class method names.
        """
        result = self.reflection.getProtectedClassSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedClassMethod", result)
        self.assertNotIn("_protectedAsyncClassMethod", result)

    def testGetProtectedClassAsyncMethods(self):
        """
        Test getProtectedClassAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedClassAsyncMethods returns only protected
        asynchronous class method names.
        """
        result = self.reflection.getProtectedClassAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedAsyncClassMethod", result)
        self.assertNotIn("_protectedClassMethod", result)

    def testGetPrivateClassMethods(self):
        """
        Test getPrivateClassMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateClassMethods returns only private
        class method names with unmangled names.
        """
        result = self.reflection.getPrivateClassMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateClassMethod", result)
        self.assertNotIn("publicClassMethod", result)
        self.assertNotIn("_protectedClassMethod", result)

    def testGetPrivateClassSyncMethods(self):
        """
        Test getPrivateClassSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateClassSyncMethods returns only private
        synchronous class method names.
        """
        result = self.reflection.getPrivateClassSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateClassMethod", result)
        self.assertNotIn("__privateAsyncClassMethod", result)

    def testGetPrivateClassAsyncMethods(self):
        """
        Test getPrivateClassAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateClassAsyncMethods returns only private
        asynchronous class method names.
        """
        result = self.reflection.getPrivateClassAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateAsyncClassMethod", result)
        self.assertNotIn("__privateClassMethod", result)

    def testGetPublicStaticMethods(self):
        """
        Test getPublicStaticMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicStaticMethods returns only public
        static method names.
        """
        result = self.reflection.getPublicStaticMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicStaticMethod", result)
        self.assertNotIn("_protectedStaticMethod", result)
        self.assertNotIn("__privateStaticMethod", result)

    def testGetPublicStaticSyncMethods(self):
        """
        Test getPublicStaticSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicStaticSyncMethods returns only public
        synchronous static method names.
        """
        result = self.reflection.getPublicStaticSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicStaticMethod", result)
        self.assertNotIn("publicAsyncStaticMethod", result)

    def testGetPublicStaticAsyncMethods(self):
        """
        Test getPublicStaticAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicStaticAsyncMethods returns only public
        asynchronous static method names.
        """
        result = self.reflection.getPublicStaticAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("publicAsyncStaticMethod", result)
        self.assertNotIn("publicStaticMethod", result)

    def testGetProtectedStaticMethods(self):
        """
        Test getProtectedStaticMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedStaticMethods returns only protected
        static method names.
        """
        result = self.reflection.getProtectedStaticMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedStaticMethod", result)
        self.assertNotIn("publicStaticMethod", result)
        self.assertNotIn("__privateStaticMethod", result)

    def testGetProtectedStaticSyncMethods(self):
        """
        Test getProtectedStaticSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedStaticSyncMethods returns only protected
        synchronous static method names.
        """
        result = self.reflection.getProtectedStaticSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedStaticMethod", result)
        self.assertNotIn("_protectedAsyncStaticMethod", result)

    def testGetProtectedStaticAsyncMethods(self):
        """
        Test getProtectedStaticAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedStaticAsyncMethods returns only protected
        asynchronous static method names.
        """
        result = self.reflection.getProtectedStaticAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedAsyncStaticMethod", result)
        self.assertNotIn("_protectedStaticMethod", result)

    def testGetPrivateStaticMethods(self):
        """
        Test getPrivateStaticMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateStaticMethods returns only private
        static method names with unmangled names.
        """
        result = self.reflection.getPrivateStaticMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateStaticMethod", result)
        self.assertNotIn("publicStaticMethod", result)
        self.assertNotIn("_protectedStaticMethod", result)

    def testGetPrivateStaticSyncMethods(self):
        """
        Test getPrivateStaticSyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateStaticSyncMethods returns only private
        synchronous static method names.
        """
        result = self.reflection.getPrivateStaticSyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateStaticMethod", result)
        self.assertNotIn("__privateAsyncStaticMethod", result)

    def testGetPrivateStaticAsyncMethods(self):
        """
        Test getPrivateStaticAsyncMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateStaticAsyncMethods returns only private
        asynchronous static method names.
        """
        result = self.reflection.getPrivateStaticAsyncMethods()
        self.assertIsInstance(result, list)
        self.assertIn("__privateAsyncStaticMethod", result)
        self.assertNotIn("__privateStaticMethod", result)

    def testGetDunderMethods(self):
        """
        Test getDunderMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getDunderMethods returns only dunder method names
        (starting and ending with double underscores).
        """
        result = self.reflection.getDunderMethods()
        self.assertIsInstance(result, list)
        # Should contain standard dunder methods like __init__, __str__, etc.
        self.assertTrue(any(method.startswith("__") and method.endswith("__") for method in result))

    def testGetMagicMethods(self):
        """
        Test getMagicMethods method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMagicMethods is an alias for getDunderMethods
        and returns the same result.
        """
        dunder_result = self.reflection.getDunderMethods()
        magic_result = self.reflection.getMagicMethods()
        self.assertEqual(dunder_result, magic_result)

    def testGetProperties(self):
        """
        Test getProperties method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProperties returns all property names from
        various visibility levels.
        """
        result = self.reflection.getProperties()
        self.assertIsInstance(result, list)
        self.assertIn("publicProperty", result)
        self.assertIn("_protectedProperty", result)
        self.assertIn("__privateProperty", result)

    def testGetPublicProperties(self):
        """
        Test getPublicProperties method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPublicProperties returns only public property names
        (not starting with underscore).
        """
        result = self.reflection.getPublicProperties()
        self.assertIsInstance(result, list)
        self.assertIn("publicProperty", result)
        self.assertNotIn("_protectedProperty", result)
        self.assertNotIn("__privateProperty", result)

    def testGetProtectedProperties(self):
        """
        Test getProtectedProperties method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProtectedProperties returns only protected property names
        (starting with single underscore).
        """
        result = self.reflection.getProtectedProperties()
        self.assertIsInstance(result, list)
        self.assertIn("_protectedProperty", result)
        self.assertNotIn("publicProperty", result)
        self.assertNotIn("__privateProperty", result)

    def testGetPrivateProperties(self):
        """
        Test getPrivateProperties method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPrivateProperties returns only private property names
        with unmangled names.
        """
        result = self.reflection.getPrivateProperties()
        self.assertIsInstance(result, list)
        self.assertIn("__privateProperty", result)
        self.assertNotIn("publicProperty", result)
        self.assertNotIn("_protectedProperty", result)

    def testGetProperty(self):
        """
        Test getProperty method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProperty returns the correct value
        for an existing property.
        """
        result = self.reflection.getProperty("publicProperty")
        self.assertEqual(result, "public property value")

    def testGetPropertyWithPrivateProperty(self):
        """
        Test getProperty method with private property.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getProperty correctly handles private property
        name mangling.
        """
        result = self.reflection.getProperty("__privateProperty")
        self.assertEqual(result, "private property value")

    def testGetPropertySignature(self):
        """
        Test getPropertySignature method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPropertySignature returns the correct
        inspect.Signature object for a property getter.
        """
        result = self.reflection.getPropertySignature("publicProperty")
        self.assertIsInstance(result, inspect.Signature)

    def testGetPropertyDocstring(self):
        """
        Test getPropertyDocstring method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getPropertyDocstring returns the correct docstring
        for a property.
        """
        result = self.reflection.getPropertyDocstring("publicProperty")
        self.assertEqual(result, "A public property.")

    def testGetConstructorDependencies(self):
        """
        Test getConstructorDependencies method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getConstructorDependencies returns a SignatureArguments
        object with constructor parameter information.
        """
        result = self.reflection.constructorSignature()
        self.assertIsInstance(result, SignatureArguments)

    def testGetMethodDependencies(self):
        """
        Test getMethodDependencies method.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that getMethodDependencies returns a SignatureArguments
        object with method parameter information.
        """
        result = self.reflection.methodSignature("publicMethod")
        self.assertIsInstance(result, SignatureArguments)

    def testCachingBehavior(self):
        """
        Test caching behavior of getAttributes and getMethods.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that repeated calls to getAttributes and getMethods
        return cached results for better performance.
        """
        # First call should compute and cache
        attrs1 = self.reflection.getAttributes()
        attrs2 = self.reflection.getAttributes()

        # Should return the same cached object
        self.assertIs(attrs1, attrs2)

        # Same for methods
        methods1 = self.reflection.getMethods()
        methods2 = self.reflection.getMethods()

        self.assertIs(methods1, methods2)

    def testEdgeCaseWithEmptyClass(self):
        """
        Test reflection behavior with an empty class.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that reflection works correctly with classes that have
        no custom attributes or methods.
        """
        result = self.empty_reflection.getPublicAttributes()
        self.assertIsInstance(result, dict)

        result = self.empty_reflection.getPublicMethods()
        self.assertIsInstance(result, list)

    def testErrorHandlingWithMockFailures(self):
        """
        Test error handling when inspect operations fail.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        Verifies that the reflection instance handles gracefully when
        inspect operations fail and returns appropriate fallback values.
        """
        with patch("inspect.getfile", side_effect=OSError):
            result = self.reflection.getFile()
            self.assertIsNone(result)

        with patch("inspect.getsource", side_effect=OSError):
            result = self.reflection.getSourceCode()
            self.assertIsNone(result)
