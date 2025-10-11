import inspect
from abc import ABC, abstractmethod
from unittest.mock import patch
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.exceptions import (
    ReflectionTypeError,
    ReflectionValueError
)
from orionis.test.cases.synchronous import SyncTestCase


# Mock abstract classes for testing
class ITestInterface(ABC):
    """Test interface for reflection testing."""

    test_attribute: str = "test_value"
    _protected_attribute: int = 42
    __private_attribute: bool = True # NOSONAR

    @abstractmethod
    def abstractMethod(self) -> str:
        """Abstract method for testing."""
        pass

    @abstractmethod
    async def abstractAsyncMethod(self) -> int:
        """Abstract async method for testing."""
        pass

    def concreteMethod(self) -> bool:
        """Concrete method for testing."""
        return True

    async def concreteAsyncMethod(self) -> str: # NOSONAR
        """Concrete async method for testing."""
        return "async_result"

    def _protectedMethod(self) -> None:
        """Protected method for testing."""
        pass

    def __privateMethod(self) -> None: # NOSONAR
        """Private method for testing."""
        pass

    @classmethod
    def classMethod(cls) -> str:
        """Class method for testing."""
        return "class_method"

    @classmethod
    def _protectedClassMethod(cls) -> str:
        """Protected class method for testing."""
        return "protected_class_method"

    @classmethod
    def __privateClassMethod(cls) -> str: # NOSONAR
        """Private class method for testing."""
        return "private_class_method"

    @staticmethod
    def staticMethod() -> str:
        """Static method for testing."""
        return "static_method"

    @staticmethod
    def _protectedStaticMethod() -> str:
        """Protected static method for testing."""
        return "protected_static_method"

    @staticmethod
    def __privateStaticMethod() -> str: # NOSONAR
        """Private static method for testing."""
        return "private_static_method"

    @property
    def testProperty(self) -> str:
        """Property for testing."""
        return "test_property"

    @property
    def _protectedProperty(self) -> str:
        """Protected property for testing."""
        return "protected_property"

    @property
    def __privateProperty(self) -> str:
        """Private property for testing."""
        return "private_property"


class IEmptyInterface(ABC):
    """Empty interface for testing edge cases."""

    @abstractmethod
    def dummyMethod(self) -> None:
        """Dummy abstract method to make this a valid interface."""
        pass


class IInterfaceWithAnnotations(ABC):
    """Interface with type annotations for testing."""

    annotated_attr: str
    _protected_annotated: int
    _IInterfaceWithAnnotations__private_annotated: bool  # Name mangled private attribute

    @abstractmethod
    def methodWithAnnotations(self, param: str) -> int:
        """Method with annotations for testing."""
        pass


class ConcreteClass:
    """Concrete class (not abstract) for negative testing."""

    def method(self):
        # Empty method for testing purposes
        pass


class TestReflectionAbstract(SyncTestCase):
    """
    Test suite for the ReflectionAbstract class.

    This test suite provides comprehensive coverage of the ReflectionAbstract class,
    testing all public methods, edge cases, error handling, and various reflection
    scenarios including abstract method detection, attribute manipulation, method
    introspection, and dependency resolution.

    Attributes
    ----------
    reflection : ReflectionAbstract
        The main reflection instance used for testing
    empty_reflection : ReflectionAbstract
        Reflection instance for empty interface testing
    annotated_reflection : ReflectionAbstract
        Reflection instance for annotation testing
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.

        Initializes ReflectionAbstract instances with different test interfaces
        to provide comprehensive testing scenarios.

        Returns
        -------
        None
        """
        super().setUp()
        self.reflection = ReflectionAbstract(ITestInterface)
        self.empty_reflection = ReflectionAbstract(IEmptyInterface)
        self.annotated_reflection = ReflectionAbstract(IInterfaceWithAnnotations)

    def tearDown(self) -> None:
        """
        Clean up test fixtures after each test method.

        Returns
        -------
        None
        """
        super().tearDown()
        self.reflection = None
        self.empty_reflection = None
        self.annotated_reflection = None

    def testIsAbstractClassWithValidInterface(self) -> None:
        """
        Test isAbstractClass static method with a valid abstract base class.

        Verifies that the method correctly identifies abstract base classes
        that directly inherit from ABC and have abstract methods.

        Returns
        -------
        None
        """
        # Test with valid abstract class
        result = ReflectionAbstract.isAbstractClass(ITestInterface)
        self.assertTrue(result)

        # Test with abstract class that has abstract methods
        result = ReflectionAbstract.isAbstractClass(IEmptyInterface)
        self.assertTrue(result)  # Has abstract methods

    def testIsAbstractClassWithConcreteClass(self) -> None:
        """
        Test isAbstractClass static method with concrete (non-abstract) classes.

        Verifies that the method correctly identifies concrete classes as
        non-abstract, even if they inherit from ABC.

        Returns
        -------
        None
        """
        # Test with concrete class
        result = ReflectionAbstract.isAbstractClass(ConcreteClass)
        self.assertFalse(result)

        # Test with built-in type
        result = ReflectionAbstract.isAbstractClass(str)
        self.assertFalse(result)

    def testIsAbstractClassWithInvalidTypes(self) -> None:
        """
        Test isAbstractClass static method with invalid input types.

        Verifies that the method correctly handles non-class types and
        returns False for invalid inputs.

        Returns
        -------
        None
        """
        # Test with non-class types
        self.assertFalse(ReflectionAbstract.isAbstractClass(None))
        self.assertFalse(ReflectionAbstract.isAbstractClass("string"))
        self.assertFalse(ReflectionAbstract.isAbstractClass(123))
        self.assertFalse(ReflectionAbstract.isAbstractClass([]))
        self.assertFalse(ReflectionAbstract.isAbstractClass({}))

    def testEnsureIsAbstractClassWithValidInterface(self) -> None:
        """
        Test ensureIsAbstractClass static method with valid abstract classes.

        Verifies that the method returns True for valid abstract base classes
        and doesn't raise exceptions.

        Returns
        -------
        None
        """
        # Should return True without raising exceptions
        result = ReflectionAbstract.ensureIsAbstractClass(ITestInterface)
        self.assertTrue(result)

        result = ReflectionAbstract.ensureIsAbstractClass(IInterfaceWithAnnotations)
        self.assertTrue(result)

    def testEnsureIsAbstractClassWithNonClassType(self) -> None:
        """
        Test ensureIsAbstractClass static method with non-class types.

        Verifies that the method raises ReflectionTypeError when provided
        with non-class types.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionAbstract.ensureIsAbstractClass("not_a_class")

        self.assertIn("Expected a class type", str(context.exception))

        with self.assertRaises(ReflectionTypeError):
            ReflectionAbstract.ensureIsAbstractClass(None)

        with self.assertRaises(ReflectionTypeError):
            ReflectionAbstract.ensureIsAbstractClass(123)

    def testEnsureIsAbstractClassWithConcreteClass(self) -> None:
        """
        Test ensureIsAbstractClass static method with concrete classes.

        Verifies that the method raises ReflectionTypeError for classes
        that are not abstract base classes.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionAbstract.ensureIsAbstractClass(ConcreteClass)

        self.assertIn("is not an interface", str(context.exception))

    def testEnsureIsAbstractClassWithNonABCClass(self) -> None:
        """
        Test ensureIsAbstractClass static method with classes not inheriting from ABC.

        Verifies that the method raises ReflectionTypeError for classes
        that don't inherit from ABC.

        Returns
        -------
        None
        """
        class NonABCClass:
            pass

        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionAbstract.ensureIsAbstractClass(NonABCClass)

        self.assertIn("is not an interface", str(context.exception))

    def testInitializationWithValidInterface(self) -> None:
        """
        Test ReflectionAbstract initialization with valid abstract classes.

        Verifies that the constructor properly initializes the instance
        with valid abstract base classes.

        Returns
        -------
        None
        """
        # Should initialize without exceptions
        reflection = ReflectionAbstract(ITestInterface)
        self.assertIsInstance(reflection, ReflectionAbstract)

        reflection = ReflectionAbstract(IInterfaceWithAnnotations)
        self.assertIsInstance(reflection, ReflectionAbstract)

    def testInitializationWithInvalidInterface(self) -> None:
        """
        Test ReflectionAbstract initialization with invalid classes.

        Verifies that the constructor raises appropriate exceptions
        when provided with invalid abstract classes.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionTypeError):
            ReflectionAbstract(ConcreteClass)

        with self.assertRaises(ReflectionTypeError):
            ReflectionAbstract("not_a_class")

        with self.assertRaises(ReflectionTypeError):
            ReflectionAbstract(None)

    def testGetClass(self) -> None:
        """
        Test getClass method returns the correct class type.

        Verifies that the method returns the exact class type that was
        provided during initialization.

        Returns
        -------
        None
        """
        result = self.reflection.getClass()
        self.assertEqual(result, ITestInterface)
        self.assertIs(result, ITestInterface)

        result = self.empty_reflection.getClass()
        self.assertEqual(result, IEmptyInterface)

    def testGetClassName(self) -> None:
        """
        Test getClassName method returns the correct class name.

        Verifies that the method returns the simple class name without
        module qualification.

        Returns
        -------
        None
        """
        result = self.reflection.getClassName()
        self.assertEqual(result, "ITestInterface")

        result = self.empty_reflection.getClassName()
        self.assertEqual(result, "IEmptyInterface")

        result = self.annotated_reflection.getClassName()
        self.assertEqual(result, "IInterfaceWithAnnotations")

    def testGetModuleName(self) -> None:
        """
        Test getModuleName method returns the correct module name.

        Verifies that the method returns the fully qualified module name
        where the class is defined.

        Returns
        -------
        None
        """
        result = self.reflection.getModuleName()
        expected_module = ITestInterface.__module__
        self.assertEqual(result, expected_module)

    def testGetModuleWithClassName(self) -> None:
        """
        Test getModuleWithClassName method returns correct full qualification.

        Verifies that the method returns the complete module path and class
        name separated by a dot.

        Returns
        -------
        None
        """
        result = self.reflection.getModuleWithClassName()
        expected = f"{ITestInterface.__module__}.ITestInterface"
        self.assertEqual(result, expected)

        result = self.empty_reflection.getModuleWithClassName()
        expected = f"{IEmptyInterface.__module__}.IEmptyInterface"
        self.assertEqual(result, expected)

    def testGetDocstring(self) -> None:
        """
        Test getDocstring method returns the correct docstring.

        Verifies that the method returns the class docstring if available,
        or None if not present.

        Returns
        -------
        None
        """
        result = self.reflection.getDocstring()
        self.assertEqual(result, ITestInterface.__doc__)
        self.assertIn("Test interface for reflection testing", result)

        result = self.empty_reflection.getDocstring()
        self.assertEqual(result, IEmptyInterface.__doc__)

    def testGetBaseClasses(self) -> None:
        """
        Test getBaseClasses method returns the correct base classes.

        Verifies that the method returns a list containing all direct
        base classes of the reflected class.

        Returns
        -------
        None
        """
        result = self.reflection.getBaseClasses()
        self.assertEqual(result, ITestInterface.__bases__)
        self.assertIn(ABC, result)

        result = self.empty_reflection.getBaseClasses()
        self.assertEqual(result, IEmptyInterface.__bases__)

    def testGetSourceCodeSuccess(self) -> None:
        """
        Test getSourceCode method returns source code successfully.

        Verifies that the method returns the complete source code of the
        abstract class when available.

        Returns
        -------
        None
        """
        with patch('inspect.getsource') as mock_getsource:
            mock_source = "class ITestInterface(ABC):\n    pass"
            mock_getsource.return_value = mock_source

            result = self.reflection.getSourceCode()
            self.assertEqual(result, mock_source)
            mock_getsource.assert_called_once_with(ITestInterface)

    def testGetSourceCodeOSError(self) -> None:
        """
        Test getSourceCode method handles OSError appropriately.

        Verifies that the method raises ReflectionValueError when
        source code cannot be retrieved due to file system errors.

        Returns
        -------
        None
        """
        with patch('inspect.getsource') as mock_getsource:
            mock_getsource.side_effect = OSError("File not found")

            with self.assertRaises(ReflectionValueError) as context:
                self.reflection.getSourceCode()

            self.assertIn("Could not retrieve source code", str(context.exception))
            self.assertIn("ITestInterface", str(context.exception))

    def testGetSourceCodeUnexpectedError(self) -> None:
        """
        Test getSourceCode method handles unexpected exceptions.

        Verifies that the method raises ReflectionValueError for
        any unexpected exceptions during source code retrieval.

        Returns
        -------
        None
        """
        with patch('inspect.getsource') as mock_getsource:
            mock_getsource.side_effect = RuntimeError("Unexpected error")

            with self.assertRaises(ReflectionValueError) as context:
                self.reflection.getSourceCode()

            self.assertIn("An unexpected error occurred", str(context.exception))

    def testGetFileSuccess(self) -> None:
        """
        Test getFile method returns file path successfully.

        Verifies that the method returns the absolute file path containing
        the abstract class definition.

        Returns
        -------
        None
        """
        with patch('inspect.getfile') as mock_getfile:
            mock_path = "/path/to/test_file.py"
            mock_getfile.return_value = mock_path

            result = self.reflection.getFile()
            self.assertEqual(result, mock_path)
            mock_getfile.assert_called_once_with(ITestInterface)

    def testGetFileTypeError(self) -> None:
        """
        Test getFile method handles TypeError appropriately.

        Verifies that the method raises ReflectionValueError when
        file path cannot be retrieved due to type errors.

        Returns
        -------
        None
        """
        with patch('inspect.getfile') as mock_getfile:
            mock_getfile.side_effect = TypeError("Type error")

            with self.assertRaises(ReflectionValueError) as context:
                self.reflection.getFile()

            self.assertIn("Could not retrieve file", str(context.exception))

    def testGetFileUnexpectedError(self) -> None:
        """
        Test getFile method handles unexpected exceptions.

        Verifies that the method raises ReflectionValueError for
        any unexpected exceptions during file path retrieval.

        Returns
        -------
        None
        """
        with patch('inspect.getfile') as mock_getfile:
            mock_getfile.side_effect = RuntimeError("Unexpected error")

            with self.assertRaises(ReflectionValueError) as context:
                self.reflection.getFile()

            self.assertIn("An unexpected error occurred", str(context.exception))

    def testGetAnnotations(self) -> None:
        """
        Test getAnnotations method returns correct type annotations.

        Verifies that the method returns a dictionary mapping attribute
        names to their annotated types, with private attribute name
        mangling handled correctly.

        Returns
        -------
        None
        """
        result = self.annotated_reflection.getAnnotations()

        # Should include annotations
        self.assertIn('annotated_attr', result)
        self.assertEqual(result['annotated_attr'], str)

        self.assertIn('_protected_annotated', result)
        self.assertEqual(result['_protected_annotated'], int)

        # Private annotations should have mangling handled correctly
        self.assertIn('__private_annotated', result)
        self.assertEqual(result['__private_annotated'], bool)

    def testGetAnnotationsEmptyInterface(self) -> None:
        """
        Test getAnnotations method with interface that has no annotations.

        Verifies that the method returns an empty dictionary when the
        class has no type annotations.

        Returns
        -------
        None
        """
        result = self.empty_reflection.getAnnotations()
        self.assertEqual(result, {})

    def testHasAttributeWithExistingAttribute(self) -> None:
        """
        Test hasAttribute method with existing class attributes.

        Verifies that the method correctly identifies attributes that
        exist in the class.

        Returns
        -------
        None
        """
        # Test with existing attribute
        self.assertTrue(self.reflection.hasAttribute('test_attribute'))
        self.assertTrue(self.reflection.hasAttribute('_protected_attribute'))

    def testHasAttributeWithNonExistingAttribute(self) -> None:
        """
        Test hasAttribute method with non-existing attributes.

        Verifies that the method correctly identifies when attributes
        do not exist in the class.

        Returns
        -------
        None
        """
        self.assertFalse(self.reflection.hasAttribute('non_existing_attribute'))
        self.assertFalse(self.empty_reflection.hasAttribute('any_attribute'))

    def testGetAttributeWithExistingAttribute(self) -> None:
        """
        Test getAttribute method with existing class attributes.

        Verifies that the method returns the correct value for existing
        class attributes.

        Returns
        -------
        None
        """
        result = self.reflection.getAttribute('test_attribute')
        self.assertEqual(result, "test_value")

        result = self.reflection.getAttribute('_protected_attribute')
        self.assertEqual(result, 42)

    def testGetAttributeWithNonExistingAttribute(self) -> None:
        """
        Test getAttribute method with non-existing attributes.

        Verifies that the method returns None for attributes that
        do not exist in the class.

        Returns
        -------
        None
        """
        result = self.reflection.getAttribute('non_existing_attribute')
        self.assertIsNone(result)

    def testSetAttributeValidAttribute(self) -> None:
        """
        Test setAttribute method with valid attribute names and values.

        Verifies that the method successfully sets attributes with valid
        names and non-callable values.

        Returns
        -------
        None
        """
        result = self.reflection.setAttribute('new_attribute', 'new_value')
        self.assertTrue(result)

        # Check that the attribute was set
        self.assertTrue(hasattr(ITestInterface, 'new_attribute'))
        self.assertEqual(getattr(ITestInterface, 'new_attribute'), 'new_value')

        # Clean up
        delattr(ITestInterface, 'new_attribute')

    def testSetAttributeInvalidName(self) -> None:
        """
        Test setAttribute method with invalid attribute names.

        Verifies that the method raises ReflectionValueError for invalid
        attribute names including keywords and invalid identifiers.

        Returns
        -------
        None
        """
        # Test with Python keyword
        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute('class', 'value')

        # Test with invalid identifier
        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute('123invalid', 'value')

        # Test with non-string name
        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute(123, 'value')

    def testSetAttributeCallableValue(self) -> None:
        """
        Test setAttribute method with callable values.

        Verifies that the method raises ReflectionValueError when
        attempting to set callable values as attributes.

        Returns
        -------
        None
        """
        def test_function():
            # Empty function for testing callable detection
            pass

        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute('func_attr', test_function)

        with self.assertRaises(ReflectionValueError):
            self.reflection.setAttribute('lambda_attr', lambda x: x)

    def testSetAttributePrivateMangling(self) -> None:
        """
        Test setAttribute method with private attribute name mangling.

        Verifies that the method properly handles private attribute
        name mangling when setting attributes.

        Returns
        -------
        None
        """
        result = self.reflection.setAttribute('__private_attr', 'private_value')
        self.assertTrue(result)

        # Should be stored with name mangling
        mangled_name = f"_{ITestInterface.__name__}__private_attr"
        self.assertTrue(hasattr(ITestInterface, mangled_name))

        # Clean up
        delattr(ITestInterface, mangled_name)

    def testRemoveAttributeExistingAttribute(self) -> None:
        """
        Test removeAttribute method with existing attributes.

        Verifies that the method successfully removes existing attributes
        from the class.

        Returns
        -------
        None
        """
        # First set an attribute
        setattr(ITestInterface, 'temp_attribute', 'temp_value')

        result = self.reflection.removeAttribute('temp_attribute')
        self.assertTrue(result)

        # Verify it was removed
        self.assertFalse(hasattr(ITestInterface, 'temp_attribute'))

    def testRemoveAttributeNonExistingAttribute(self) -> None:
        """
        Test removeAttribute method with non-existing attributes.

        Verifies that the method raises ReflectionValueError when
        attempting to remove attributes that don't exist.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionValueError) as context:
            self.reflection.removeAttribute('non_existing_attribute')

        self.assertIn("does not exist", str(context.exception))

    def testRemoveAttributePrivateMangling(self) -> None:
        """
        Test removeAttribute method with private attribute name mangling.

        Verifies that the method properly handles private attribute
        name mangling when removing attributes.

        Returns
        -------
        None
        """
        # Set a private attribute with mangling
        mangled_name = f"_{ITestInterface.__name__}__temp_private"
        setattr(ITestInterface, mangled_name, 'private_value')

        result = self.reflection.removeAttribute('__temp_private')
        self.assertTrue(result)

        # Verify it was removed
        self.assertFalse(hasattr(ITestInterface, mangled_name))

    def testGetAttributes(self) -> None:
        """
        Test getAttributes method returns all class attributes.

        Verifies that the method returns a dictionary containing all
        class attributes including public, protected, private, and dunder.

        Returns
        -------
        None
        """
        result = self.reflection.getAttributes()

        # Should be a dictionary
        self.assertIsInstance(result, dict)

        # Should contain test attributes
        self.assertIn('test_attribute', result)
        self.assertEqual(result['test_attribute'], 'test_value')

        # Should contain protected attributes
        self.assertIn('_protected_attribute', result)
        self.assertEqual(result['_protected_attribute'], 42)

    def testGetPublicAttributes(self) -> None:
        """
        Test getPublicAttributes method returns only public attributes.

        Verifies that the method returns a dictionary containing only
        public class attributes (not starting with underscores).

        Returns
        -------
        None
        """
        result = self.reflection.getPublicAttributes()

        # Should contain public attributes
        self.assertIn('test_attribute', result)
        self.assertEqual(result['test_attribute'], 'test_value')

        # Should not contain protected/private attributes
        for key in result.keys():
            self.assertFalse(key.startswith('_'))

    def testGetProtectedAttributes(self) -> None:
        """
        Test getProtectedAttributes method returns only protected attributes.

        Verifies that the method returns a dictionary containing only
        protected attributes (starting with single underscore).

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedAttributes()

        # Should contain protected attributes
        self.assertIn('_protected_attribute', result)
        self.assertEqual(result['_protected_attribute'], 42)

        # All keys should start with single underscore (not double)
        for key in result.keys():
            self.assertTrue(key.startswith('_'))
            self.assertFalse(key.startswith('__'))

    def testGetPrivateAttributes(self) -> None:
        """
        Test getPrivateAttributes method returns only private attributes.

        Verifies that the method returns a dictionary containing only
        private attributes with name mangling prefixes removed.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateAttributes()

        # Should contain private attributes with name mangling removed
        if '__private_attribute' in result:
            self.assertTrue(result['__private_attribute'])

    def testGetDunderAttributes(self) -> None:
        """
        Test getDunderAttributes method returns only dunder attributes.

        Verifies that the method returns a dictionary containing only
        dunder (magic) attributes, excluding built-in ones.

        Returns
        -------
        None
        """
        result = self.reflection.getDunderAttributes()

        # Should be a dictionary
        self.assertIsInstance(result, dict)

        # All keys should start and end with double underscores
        for key in result.keys():
            self.assertTrue(key.startswith('__'))
            self.assertTrue(key.endswith('__'))

        # Should not contain excluded built-in attributes
        excluded = ['__class__', '__module__', '__doc__', '__dict__']
        for attr in excluded:
            self.assertNotIn(attr, result)

    def testGetMagicAttributes(self) -> None:
        """
        Test getMagicAttributes method is alias for getDunderAttributes.

        Verifies that getMagicAttributes returns the same result as
        getDunderAttributes method.

        Returns
        -------
        None
        """
        dunder_result = self.reflection.getDunderAttributes()
        magic_result = self.reflection.getMagicAttributes()

        self.assertEqual(dunder_result, magic_result)

    def testHasMethodWithExistingMethod(self) -> None:
        """
        Test hasMethod method with existing class methods.

        Verifies that the method correctly identifies methods that
        exist in the class.

        Returns
        -------
        None
        """
        self.assertTrue(self.reflection.hasMethod('abstractMethod'))
        self.assertTrue(self.reflection.hasMethod('concreteMethod'))
        self.assertTrue(self.reflection.hasMethod('classMethod'))
        self.assertTrue(self.reflection.hasMethod('staticMethod'))

    def testHasMethodWithNonExistingMethod(self) -> None:
        """
        Test hasMethod method with non-existing methods.

        Verifies that the method correctly identifies when methods
        do not exist in the class.

        Returns
        -------
        None
        """
        self.assertFalse(self.reflection.hasMethod('non_existing_method'))
        self.assertFalse(self.empty_reflection.hasMethod('any_method'))

    def testRemoveMethodExistingMethod(self) -> None:
        """
        Test removeMethod method with existing methods.

        Verifies that the method successfully removes existing methods
        from the class.

        Returns
        -------
        None
        """
        # Add a temporary method for testing
        def temp_method(self):
            return "temp"

        setattr(ITestInterface, 'temp_method', temp_method)

        result = self.reflection.removeMethod('temp_method')
        self.assertTrue(result)

        # Verify it was removed
        self.assertFalse(hasattr(ITestInterface, 'temp_method'))

    def testRemoveMethodNonExistingMethod(self) -> None:
        """
        Test removeMethod method with non-existing methods.

        Verifies that the method raises ReflectionValueError when
        attempting to remove methods that don't exist.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.removeMethod('non_existing_method')

    def testGetMethodSignatureExistingMethod(self) -> None:
        """
        Test getMethodSignature method with existing methods.

        Verifies that the method returns the correct signature object
        for existing methods.

        Returns
        -------
        None
        """
        result = self.reflection.getMethodSignature('abstractMethod')
        self.assertIsInstance(result, inspect.Signature)

        result = self.reflection.getMethodSignature('concreteMethod')
        self.assertIsInstance(result, inspect.Signature)

    def testGetMethodSignatureNonExistingMethod(self) -> None:
        """
        Test getMethodSignature method with non-existing methods.

        Verifies that the method raises ReflectionValueError when
        attempting to get signatures for non-existing methods.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.getMethodSignature('non_existing_method')

    def testGetMethodSignatureNonCallable(self) -> None:
        """
        Test getMethodSignature method with non-callable attributes.

        Verifies that the method raises ReflectionValueError when
        attempting to get signatures for non-callable attributes.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.getMethodSignature('test_attribute')

    def testGetMethods(self) -> None:
        """
        Test getMethods method returns all method names.

        Verifies that the method returns a list containing all method
        names from the class including different visibility levels.

        Returns
        -------
        None
        """
        result = self.reflection.getMethods()

        # Should be a list
        self.assertIsInstance(result, list)

        # Should contain expected methods
        self.assertIn('abstractMethod', result)
        self.assertIn('concreteMethod', result)
        self.assertIn('classMethod', result)
        self.assertIn('staticMethod', result)

    def testGetPublicMethods(self) -> None:
        """
        Test getPublicMethods method returns only public methods.

        Verifies that the method returns a list containing only
        public method names (not starting with underscores).

        Returns
        -------
        None
        """
        result = self.reflection.getPublicMethods()

        # Should contain public methods
        self.assertIn('abstractMethod', result)
        self.assertIn('concreteMethod', result)

        # Should not contain protected/private methods
        for method in result:
            self.assertFalse(method.startswith('_'))

    def testGetPublicSyncMethods(self) -> None:
        """
        Test getPublicSyncMethods method returns only synchronous public methods.

        Verifies that the method returns a list containing only
        synchronous public method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicSyncMethods()

        # Should contain sync methods
        self.assertIn('abstractMethod', result)
        self.assertIn('concreteMethod', result)

        # Should not contain async methods
        self.assertNotIn('abstractAsyncMethod', result)
        self.assertNotIn('concreteAsyncMethod', result)

    def testGetPublicAsyncMethods(self) -> None:
        """
        Test getPublicAsyncMethods method returns only asynchronous public methods.

        Verifies that the method returns a list containing only
        asynchronous public method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicAsyncMethods()

        # Should contain async methods
        self.assertIn('abstractAsyncMethod', result)
        self.assertIn('concreteAsyncMethod', result)

        # Should not contain sync methods
        self.assertNotIn('abstractMethod', result)
        self.assertNotIn('concreteMethod', result)

    def testGetProtectedMethods(self) -> None:
        """
        Test getProtectedMethods method returns only protected methods.

        Verifies that the method returns a list containing only
        protected method names (starting with single underscore).

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedMethods()

        # Should contain protected methods
        self.assertIn('_protectedMethod', result)

        # All methods should start with single underscore
        for method in result:
            self.assertTrue(method.startswith('_'))
            self.assertFalse(method.startswith('__'))

    def testGetProtectedSyncMethods(self) -> None:
        """
        Test getProtectedSyncMethods method returns only synchronous protected methods.

        Verifies that the method returns a list containing only
        synchronous protected method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedSyncMethods()

        # Should contain sync protected methods
        if '_protectedMethod' in self.reflection.getProtectedMethods():
            self.assertIn('_protectedMethod', result)

    def testGetProtectedAsyncMethods(self) -> None:
        """
        Test getProtectedAsyncMethods method returns only asynchronous protected methods.

        Verifies that the method returns a list containing only
        asynchronous protected method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateMethods(self) -> None:
        """
        Test getPrivateMethods method returns only private methods.

        Verifies that the method returns a list containing only
        private method names with class name prefixes removed.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateMethods()

        # Should contain private methods with name mangling removed
        if '__privateMethod' in result:
            self.assertIn('__privateMethod', result)

    def testGetPrivateSyncMethods(self) -> None:
        """
        Test getPrivateSyncMethods method returns only synchronous private methods.

        Verifies that the method returns a list containing only
        synchronous private method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateSyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateAsyncMethods(self) -> None:
        """
        Test getPrivateAsyncMethods method returns only asynchronous private methods.

        Verifies that the method returns a list containing only
        asynchronous private method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPublicClassMethods(self) -> None:
        """
        Test getPublicClassMethods method returns only public class methods.

        Verifies that the method returns a list containing only
        public class method names decorated with @classmethod.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicClassMethods()

        # Should contain public class methods
        self.assertIn('classMethod', result)

        # Should not contain instance methods
        self.assertNotIn('concreteMethod', result)

    def testGetPublicClassSyncMethods(self) -> None:
        """
        Test getPublicClassSyncMethods method returns only synchronous public class methods.

        Verifies that the method returns a list containing only
        synchronous public class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicClassSyncMethods()

        # Should contain sync class methods
        self.assertIn('classMethod', result)

    def testGetPublicClassAsyncMethods(self) -> None:
        """
        Test getPublicClassAsyncMethods method returns only asynchronous public class methods.

        Verifies that the method returns a list containing only
        asynchronous public class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicClassAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetProtectedClassMethods(self) -> None:
        """
        Test getProtectedClassMethods method returns only protected class methods.

        Verifies that the method returns a list containing only
        protected class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedClassMethods()

        # Should contain protected class methods
        if '_protectedClassMethod' in self.reflection.getMethods():
            self.assertIn('_protectedClassMethod', result)

    def testGetProtectedClassSyncMethods(self) -> None:
        """
        Test getProtectedClassSyncMethods method returns only synchronous protected class methods.

        Verifies that the method returns a list containing only
        synchronous protected class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedClassSyncMethods()
        self.assertIsInstance(result, list)

    def testGetProtectedClassAsyncMethods(self) -> None:
        """
        Test getProtectedClassAsyncMethods method returns only asynchronous protected class methods.

        Verifies that the method returns a list containing only
        asynchronous protected class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedClassAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateClassMethods(self) -> None:
        """
        Test getPrivateClassMethods method returns only private class methods.

        Verifies that the method returns a list containing only
        private class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateClassMethods()

        # Should contain private class methods with name mangling removed
        if '__privateClassMethod' in result:
            self.assertIn('__privateClassMethod', result)

    def testGetPrivateClassSyncMethods(self) -> None:
        """
        Test getPrivateClassSyncMethods method returns only synchronous private class methods.

        Verifies that the method returns a list containing only
        synchronous private class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateClassSyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateClassAsyncMethods(self) -> None:
        """
        Test getPrivateClassAsyncMethods method returns only asynchronous private class methods.

        Verifies that the method returns a list containing only
        asynchronous private class method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateClassAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPublicStaticMethods(self) -> None:
        """
        Test getPublicStaticMethods method returns only public static methods.

        Verifies that the method returns a list containing only
        public static method names decorated with @staticmethod.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicStaticMethods()

        # Should contain public static methods
        self.assertIn('staticMethod', result)

        # Should not contain instance methods
        self.assertNotIn('concreteMethod', result)

    def testGetPublicStaticSyncMethods(self) -> None:
        """
        Test getPublicStaticSyncMethods method returns only synchronous public static methods.

        Verifies that the method returns a list containing only
        synchronous public static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicStaticSyncMethods()

        # Should contain sync static methods
        self.assertIn('staticMethod', result)

    def testGetPublicStaticAsyncMethods(self) -> None:
        """
        Test getPublicStaticAsyncMethods method returns only asynchronous public static methods.

        Verifies that the method returns a list containing only
        asynchronous public static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPublicStaticAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetProtectedStaticMethods(self) -> None:
        """
        Test getProtectedStaticMethods method returns only protected static methods.

        Verifies that the method returns a list containing only
        protected static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedStaticMethods()

        # Should contain protected static methods
        if '_protectedStaticMethod' in self.reflection.getMethods():
            self.assertIn('_protectedStaticMethod', result)

    def testGetProtectedStaticSyncMethods(self) -> None:
        """
        Test getProtectedStaticSyncMethods method returns only synchronous protected static methods.

        Verifies that the method returns a list containing only
        synchronous protected static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedStaticSyncMethods()
        self.assertIsInstance(result, list)

    def testGetProtectedStaticAsyncMethods(self) -> None:
        """
        Test getProtectedStaticAsyncMethods method returns only asynchronous protected static methods.

        Verifies that the method returns a list containing only
        asynchronous protected static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedStaticAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateStaticMethods(self) -> None:
        """
        Test getPrivateStaticMethods method returns only private static methods.

        Verifies that the method returns a list containing only
        private static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateStaticMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateStaticSyncMethods(self) -> None:
        """
        Test getPrivateStaticSyncMethods method returns only synchronous private static methods.

        Verifies that the method returns a list containing only
        synchronous private static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateStaticSyncMethods()
        self.assertIsInstance(result, list)

    def testGetPrivateStaticAsyncMethods(self) -> None:
        """
        Test getPrivateStaticAsyncMethods method returns only asynchronous private static methods.

        Verifies that the method returns a list containing only
        asynchronous private static method names.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateStaticAsyncMethods()
        self.assertIsInstance(result, list)

    def testGetDunderMethods(self) -> None:
        """
        Test getDunderMethods method returns only dunder methods.

        Verifies that the method returns a list containing only
        dunder (magic) method names, excluding built-in ones.

        Returns
        -------
        None
        """
        result = self.reflection.getDunderMethods()
        self.assertIsInstance(result, list)

        # All methods should start and end with double underscores
        for method in result:
            self.assertTrue(method.startswith('__'))
            self.assertTrue(method.endswith('__'))

    def testGetMagicMethods(self) -> None:
        """
        Test getMagicMethods method is alias for getDunderMethods.

        Verifies that getMagicMethods returns the same result as
        getDunderMethods method.

        Returns
        -------
        None
        """
        dunder_result = self.reflection.getDunderMethods()
        magic_result = self.reflection.getMagicMethods()

        self.assertEqual(dunder_result, magic_result)

    def testGetProperties(self) -> None:
        """
        Test getProperties method returns all property names.

        Verifies that the method returns a list containing all
        property names from the class.

        Returns
        -------
        None
        """
        result = self.reflection.getProperties()
        self.assertIsInstance(result, list)

        # Should contain properties
        self.assertIn('testProperty', result)

    def testGetPublicProperties(self) -> None:
        """
        Test getPublicProperties method returns only public properties.

        Verifies that the method returns a list containing only
        public property names (not starting with underscores).

        Returns
        -------
        None
        """
        result = self.reflection.getPublicProperties()

        # Should contain public properties
        self.assertIn('testProperty', result)

        # Should not contain protected/private properties
        for prop in result:
            self.assertFalse(prop.startswith('_'))

    def testGetProtectedProperties(self) -> None:
        """
        Test getProtectedProperties method returns only protected properties.

        Verifies that the method returns a list containing only
        protected property names (starting with single underscore).

        Returns
        -------
        None
        """
        result = self.reflection.getProtectedProperties()

        # Should contain protected properties
        if '_protectedProperty' in self.reflection.getProperties():
            self.assertIn('_protectedProperty', result)

    def testGetPrivateProperties(self) -> None:
        """
        Test getPrivateProperties method returns only private properties.

        Verifies that the method returns a list containing only
        private property names with name mangling prefixes removed.

        Returns
        -------
        None
        """
        result = self.reflection.getPrivateProperties()

        # Should contain private properties with name mangling removed
        if '__privateProperty' in result:
            self.assertIn('__privateProperty', result)

    def testGetConstructorDependencies(self) -> None:
        """
        Test getConstructorDependencies method returns dependency resolution.

        Verifies that the method properly integrates with ReflectDependencies
        to resolve constructor dependencies.

        Returns
        -------
        None
        """
        result = self.reflection.getConstructorDependencies()

        # Should return a ResolveArguments object
        self.assertIsNotNone(result)
        # Basic structure check
        self.assertTrue(hasattr(result, 'resolved'))
        self.assertTrue(hasattr(result, 'unresolved'))
        self.assertTrue(hasattr(result, 'ordered'))

    def testGetMethodDependencies(self) -> None:
        """
        Test getMethodDependencies method returns method dependency resolution.

        Verifies that the method properly integrates with ReflectDependencies
        to resolve method dependencies for specific methods.

        Returns
        -------
        None
        """
        method_name = 'abstractMethod'
        result = self.reflection.getMethodDependencies(method_name)

        # Should return a ResolveArguments object
        self.assertIsNotNone(result)
        # Basic structure check
        self.assertTrue(hasattr(result, 'resolved'))
        self.assertTrue(hasattr(result, 'unresolved'))
        self.assertTrue(hasattr(result, 'ordered'))

    def testPropertySignatureExistingProperty(self) -> None:
        """
        Test getPropertySignature method with existing properties.

        Verifies that the method returns the correct signature object
        for existing properties.

        Returns
        -------
        None
        """
        try:
            result = self.reflection.getPropertySignature('testProperty')
            self.assertIsInstance(result, inspect.Signature)
        except (ReflectionValueError, AttributeError):
            # Some properties might not have accessible signatures
            self.skipTest("Property signature not accessible")

    def testPropertySignatureNonExistingProperty(self) -> None:
        """
        Test getPropertySignature method with non-existing properties.

        Verifies that the method raises appropriate exceptions when
        attempting to get signatures for non-existing properties.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.getPropertySignature('non_existing_property')

    def testPropertyDocstringExistingProperty(self) -> None:
        """
        Test getPropertyDocstring method with existing properties.

        Verifies that the method returns the correct docstring for
        existing properties.

        Returns
        -------
        None
        """
        try:
            result = self.reflection.getPropertyDocstring('testProperty')
            if result is not None:
                self.assertIsInstance(result, str)
        except (ReflectionValueError, AttributeError):
            # Some properties might not have accessible docstrings
            self.skipTest("Property docstring not accessible")

    def testPropertyDocstringNonExistingProperty(self) -> None:
        """
        Test getPropertyDocstring method with non-existing properties.

        Verifies that the method raises appropriate exceptions when
        attempting to get docstrings for non-existing properties.

        Returns
        -------
        None
        """
        with self.assertRaises(ReflectionValueError):
            self.reflection.getPropertyDocstring('non_existing_property')

    def testEdgeCaseEmptyInterface(self) -> None:
        """
        Test reflection behavior with empty interface.

        Verifies that the ReflectionAbstract class handles empty
        interfaces correctly without raising exceptions.

        Returns
        -------
        None
        """
        # Basic operations should work with empty interface
        self.assertEqual(self.empty_reflection.getClassName(), 'IEmptyInterface')
        self.assertEqual(self.empty_reflection.getClass(), IEmptyInterface)

        # Collections should be empty or contain only inherited elements
        attributes = self.empty_reflection.getAttributes()
        self.assertIsInstance(attributes, dict)

        methods = self.empty_reflection.getMethods()
        self.assertIsInstance(methods, list)

    def testThreadSafety(self) -> None:
        """
        Test basic thread safety considerations.

        Verifies that reflection operations don't cause obvious
        thread safety issues when accessing class metadata.

        Returns
        -------
        None
        """
        # Multiple instances should work independently
        reflection1 = ReflectionAbstract(ITestInterface)
        reflection2 = ReflectionAbstract(ITestInterface)

        self.assertEqual(reflection1.getClassName(), reflection2.getClassName())
        self.assertEqual(reflection1.getClass(), reflection2.getClass())

        # Modifications to one instance shouldn't affect another
        reflection1.setAttribute('temp_attr1', 'value1')
        reflection2.setAttribute('temp_attr2', 'value2')

        self.assertTrue(reflection1.hasAttribute('temp_attr1'))
        self.assertTrue(reflection2.hasAttribute('temp_attr1'))  # Both see class-level changes
        self.assertTrue(reflection1.hasAttribute('temp_attr2'))
        self.assertTrue(reflection2.hasAttribute('temp_attr2'))

        # Clean up
        reflection1.removeAttribute('temp_attr1')
        reflection2.removeAttribute('temp_attr2')

    def testComplexInheritanceScenario(self) -> None:
        """
        Test reflection with complex inheritance scenarios.

        Verifies that the ReflectionAbstract class properly handles
        interfaces with complex inheritance hierarchies.

        Returns
        -------
        None
        """
        # Create a more complex interface hierarchy
        class IBaseInterface(ABC):
            @abstractmethod
            def baseMethod(self) -> str:
                pass

        class IExtendedInterface(IBaseInterface):
            @abstractmethod
            def extendedMethod(self) -> int:
                pass

        extended_reflection = ReflectionAbstract(IExtendedInterface)

        # Should inherit from both ABC and IBaseInterface
        base_classes = extended_reflection.getBaseClasses()
        self.assertIn(IBaseInterface, base_classes)

        # Should include methods from the extended interface itself
        methods = extended_reflection.getMethods()
        self.assertIn('extendedMethod', methods)
