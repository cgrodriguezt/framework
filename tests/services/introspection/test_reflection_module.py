import os
import sys
import tempfile
from unittest.mock import patch, mock_open
from orionis.test.cases.synchronous import SyncTestCase
from orionis.services.introspection.modules.reflection import ReflectionModule
from orionis.services.introspection.exceptions import (
    ReflectionTypeError,
    ReflectionValueError,
)

class TestReflectionModule(SyncTestCase):
    """
    Test cases for the ReflectionModule class.

    This test suite ensures comprehensive coverage of all methods and edge cases
    in the ReflectionModule class, including module import validation, class
    operations, constant and function retrieval, and error handling.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Notes
        -----
        Creates a ReflectionModule instance using the 'os' module for testing
        purposes, as it's a standard library module with predictable structure.
        """
        self.test_module_name = "os"
        self.reflection = ReflectionModule(self.test_module_name)

    def testConstructorWithValidModule(self):
        """
        Test ReflectionModule constructor with a valid module name.

        Verifies that the constructor successfully imports a valid module
        and stores it correctly.

        Notes
        -----
        Uses the 'sys' module as it's guaranteed to be available in any
        Python environment.
        """
        reflection = ReflectionModule("sys")
        self.assertIsNotNone(reflection.getModule())
        self.assertEqual(reflection.getModule().__name__, "sys")

    def testConstructorWithEmptyString(self):
        """
        Test ReflectionModule constructor with empty string.

        Verifies that passing an empty string raises ReflectionTypeError
        with appropriate error message.

        Raises
        ------
        ReflectionTypeError
            When module name is an empty string.
        """
        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionModule("")
        self.assertIn("Module name must be a non-empty string", str(context.exception))

    def testConstructorWithWhitespaceString(self):
        """
        Test ReflectionModule constructor with whitespace-only string.

        Verifies that passing a string containing only whitespace raises
        ReflectionTypeError with appropriate error message.

        Raises
        ------
        ReflectionTypeError
            When module name contains only whitespace.
        """
        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionModule("   ")
        self.assertIn("Module name must be a non-empty string", str(context.exception))

    def testConstructorWithNonStringType(self):
        """
        Test ReflectionModule constructor with non-string type.

        Verifies that passing a non-string value raises ReflectionTypeError
        with appropriate error message.

        Raises
        ------
        ReflectionTypeError
            When module name is not a string.
        """
        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionModule(123)
        self.assertIn("Module name must be a non-empty string", str(context.exception))

    def testConstructorWithNoneValue(self):
        """
        Test ReflectionModule constructor with None value.

        Verifies that passing None raises ReflectionTypeError with
        appropriate error message.

        Raises
        ------
        ReflectionTypeError
            When module name is None.
        """
        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionModule(None)
        self.assertIn("Module name must be a non-empty string", str(context.exception))

    def testConstructorWithNonExistentModule(self):
        """
        Test ReflectionModule constructor with non-existent module.

        Verifies that attempting to import a non-existent module raises
        ReflectionTypeError with appropriate error message.

        Raises
        ------
        ReflectionTypeError
            When the specified module cannot be imported.
        """
        with self.assertRaises(ReflectionTypeError) as context:
            ReflectionModule("non_existent_module_xyz123")
        self.assertIn("Failed to import module", str(context.exception))

    def testGetModule(self):
        """
        Test getModule method returns correct module object.

        Verifies that getModule returns the same module object that was
        imported during construction.
        """
        module = self.reflection.getModule()
        self.assertEqual(module.__name__, self.test_module_name)
        self.assertIs(module, os)

    def testHasClassWithExistingClass(self):
        """
        Test hasClass method with an existing class.

        Verifies that hasClass returns True when checking for a class
        that exists in the module.

        Notes
        -----
        Uses 'stat_result' class from os module as it's a known class
        in the os module.
        """
        # Create a test module with a known class
        reflection = ReflectionModule("os")
        # os.stat_result is a class in the os module
        result = reflection.hasClass("stat_result")
        self.assertTrue(result)

    def testHasClassWithNonExistentClass(self):
        """
        Test hasClass method with non-existent class.

        Verifies that hasClass returns False when checking for a class
        that does not exist in the module.
        """
        result = self.reflection.hasClass("NonExistentClass")
        self.assertFalse(result)

    def testGetClassWithExistingClass(self):
        """
        Test getClass method with an existing class.

        Verifies that getClass returns the correct class object when
        the class exists in the module.
        """
        reflection = ReflectionModule("os")
        cls = reflection.getClass("stat_result")
        self.assertIsNotNone(cls)
        self.assertIsInstance(cls, type)

    def testGetClassWithNonExistentClass(self):
        """
        Test getClass method with non-existent class.

        Verifies that getClass returns None when the specified class
        does not exist in the module.
        """
        cls = self.reflection.getClass("NonExistentClass")
        self.assertIsNone(cls)

    def testSetClassWithValidClass(self):
        """
        Test setClass method with a valid class.

        Verifies that setClass successfully adds a new class to the module
        and returns True.
        """
        class TestClass:
            pass

        result = self.reflection.setClass("TestClass", TestClass)
        self.assertTrue(result)
        self.assertTrue(self.reflection.hasClass("TestClass"))
        self.assertIs(self.reflection.getClass("TestClass"), TestClass)

    def testSetClassWithNonClassType(self):
        """
        Test setClass method with non-class type.

        Verifies that setClass raises ReflectionValueError when attempting
        to set a non-class object as a class.

        Raises
        ------
        ReflectionValueError
            When the provided object is not a class type.
        """
        with self.assertRaises(ReflectionValueError) as context:
            self.reflection.setClass("NotAClass", "string_value")
        self.assertIn("Expected a class type", str(context.exception))

    def testSetClassWithInvalidIdentifier(self):
        """
        Test setClass method with invalid identifier.

        Verifies that setClass raises ReflectionValueError when attempting
        to use an invalid Python identifier as class name.

        Raises
        ------
        ReflectionValueError
            When the class name is not a valid Python identifier.
        """
        class TestClass:
            pass

        with self.assertRaises(ReflectionValueError) as context:
            self.reflection.setClass("123InvalidName", TestClass)
        self.assertIn("Invalid class name", str(context.exception))

    def testSetClassWithReservedKeyword(self):
        """
        Test setClass method with reserved keyword.

        Verifies that setClass raises ReflectionValueError when attempting
        to use a Python reserved keyword as class name.

        Raises
        ------
        ReflectionValueError
            When the class name is a reserved Python keyword.
        """
        class TestClass:
            pass

        with self.assertRaises(ReflectionValueError) as context:
            self.reflection.setClass("class", TestClass)
        self.assertIn("is a reserved keyword", str(context.exception))

    def testRemoveClassWithExistingClass(self):
        """
        Test removeClass method with existing class.

        Verifies that removeClass successfully removes an existing class
        from the module and returns True.
        """
        # First add a class
        class TestClass:
            pass
        self.reflection.setClass("TestClass", TestClass)

        # Then remove it
        result = self.reflection.removeClass("TestClass")
        self.assertTrue(result)
        self.assertFalse(self.reflection.hasClass("TestClass"))

    def testRemoveClassWithNonExistentClass(self):
        """
        Test removeClass method with non-existent class.

        Verifies that removeClass raises ValueError when attempting to
        remove a class that does not exist in the module.

        Raises
        ------
        ValueError
            When the specified class does not exist in the module.
        """
        with self.assertRaises(ValueError) as context:
            self.reflection.removeClass("NonExistentClass")
        self.assertIn("does not exist in module", str(context.exception))

    def testInitClassWithExistingClass(self):
        """
        Test initClass method with existing class.

        Verifies that initClass successfully creates an instance of an
        existing class with the provided arguments.
        """
        # Add a test class with constructor arguments
        class TestClass:
            def __init__(self, value):
                self.value = value

        self.reflection.setClass("TestClass", TestClass)
        instance = self.reflection.initClass("TestClass", 42)
        self.assertIsInstance(instance, TestClass)
        self.assertEqual(instance.value, 42)

    def testInitClassWithNonExistentClass(self):
        """
        Test initClass method with non-existent class.

        Verifies that initClass raises ReflectionValueError when attempting
        to initialize a class that does not exist in the module.

        Raises
        ------
        ReflectionValueError
            When the specified class does not exist in the module.
        """
        with self.assertRaises(ReflectionValueError) as context:
            self.reflection.initClass("NonExistentClass")
        self.assertIn("does not exist in module", str(context.exception))

    def testInitClassWithKeywordArguments(self):
        """
        Test initClass method with keyword arguments.

        Verifies that initClass successfully passes keyword arguments to
        the class constructor.
        """
        class TestClass:
            def __init__(self, name, value=None):
                self.name = name
                self.value = value

        self.reflection.setClass("TestClass", TestClass)
        instance = self.reflection.initClass("TestClass", "test", value=42)
        self.assertIsInstance(instance, TestClass)
        self.assertEqual(instance.name, "test")
        self.assertEqual(instance.value, 42)

    def testGetClasses(self):
        """
        Test getClasses method returns dictionary of classes.

        Verifies that getClasses returns a dictionary containing all
        classes defined in the module.
        """
        classes = self.reflection.getClasses()
        self.assertIsInstance(classes, dict)
        # os module should have some classes
        self.assertGreater(len(classes), 0)
        # All values should be class types
        for cls in classes.values():
            self.assertIsInstance(cls, type)

    def testGetPublicClasses(self):
        """
        Test getPublicClasses method returns only public classes.

        Verifies that getPublicClasses returns only classes that don't
        start with underscore (public classes).
        """
        # Add test classes with different visibility
        class PublicClass:
            pass

        class _ProtectedClass:
            pass

        class __PrivateClass:
            pass

        self.reflection.setClass("PublicClass", PublicClass)
        self.reflection.setClass("_ProtectedClass", _ProtectedClass)
        self.reflection.setClass("__PrivateClass", __PrivateClass)

        public_classes = self.reflection.getPublicClasses()
        self.assertIn("PublicClass", public_classes)
        self.assertNotIn("_ProtectedClass", public_classes)
        self.assertNotIn("__PrivateClass", public_classes)

    def testGetProtectedClasses(self):
        """
        Test getProtectedClasses method returns only protected classes.

        Verifies that getProtectedClasses returns only classes that start
        with single underscore (protected classes).
        """
        # Add test classes with different visibility
        class PublicClass:
            pass

        class _ProtectedClass:
            pass

        class __PrivateClass:
            pass

        self.reflection.setClass("PublicClass", PublicClass)
        self.reflection.setClass("_ProtectedClass", _ProtectedClass)
        self.reflection.setClass("__PrivateClass", __PrivateClass)

        protected_classes = self.reflection.getProtectedClasses()
        self.assertNotIn("PublicClass", protected_classes)
        self.assertIn("_ProtectedClass", protected_classes)
        self.assertNotIn("__PrivateClass", protected_classes)

    def testGetPrivateClasses(self):
        """
        Test getPrivateClasses method returns only private classes.

        Verifies that getPrivateClasses returns only classes that start
        with double underscore but don't end with double underscore
        (private classes).
        """
        # Add test classes with different visibility
        class PublicClass:
            pass

        class _ProtectedClass:
            pass

        class __PrivateClass:
            pass

        self.reflection.setClass("PublicClass", PublicClass)
        self.reflection.setClass("_ProtectedClass", _ProtectedClass)
        self.reflection.setClass("__PrivateClass", __PrivateClass)

        private_classes = self.reflection.getPrivateClasses()
        self.assertNotIn("PublicClass", private_classes)
        self.assertNotIn("_ProtectedClass", private_classes)
        self.assertIn("__PrivateClass", private_classes)

    def testGetConstant(self):
        """
        Test getConstant method with existing constant.

        Verifies that getConstant returns the correct value for an
        existing constant in the module.
        """
        # Add a test constant to the module
        self.reflection.getModule().TEST_CONSTANT = 42
        constant_value = self.reflection.getConstant("TEST_CONSTANT")
        self.assertEqual(constant_value, 42)

    def testGetConstantWithNonExistentConstant(self):
        """
        Test getConstant method with non-existent constant.

        Verifies that getConstant returns None when the specified
        constant does not exist in the module.
        """
        constant_value = self.reflection.getConstant("NON_EXISTENT_CONSTANT")
        self.assertIsNone(constant_value)

    def testGetConstants(self):
        """
        Test getConstants method returns dictionary of constants.

        Verifies that getConstants returns a dictionary containing all
        uppercase constants defined in the module.
        """
        # Add test constants
        self.reflection.getModule().TEST_CONSTANT = 42
        self.reflection.getModule().ANOTHER_CONSTANT = "test"
        self.reflection.getModule().lowercase_var = "not_constant"

        constants = self.reflection.getConstants()
        self.assertIsInstance(constants, dict)
        self.assertIn("TEST_CONSTANT", constants)
        self.assertIn("ANOTHER_CONSTANT", constants)
        self.assertNotIn("lowercase_var", constants)

    def testGetPublicConstants(self):
        """
        Test getPublicConstants method returns only public constants.

        Verifies that getPublicConstants returns only constants that
        don't start with underscore.
        """
        # Add test constants with different visibility
        self.reflection.getModule().PUBLIC_CONSTANT = 42
        self.reflection.getModule()._PROTECTED_CONSTANT = 24
        setattr(self.reflection.getModule(), "__PRIVATE_CONSTANT", 84)

        public_constants = self.reflection.getPublicConstants()
        self.assertIn("PUBLIC_CONSTANT", public_constants)
        self.assertNotIn("_PROTECTED_CONSTANT", public_constants)
        self.assertNotIn("__PRIVATE_CONSTANT", public_constants)

    def testGetProtectedConstants(self):
        """
        Test getProtectedConstants method returns only protected constants.

        Verifies that getProtectedConstants returns only constants that
        start with single underscore.
        """
        # Add test constants with different visibility
        self.reflection.getModule().PUBLIC_CONSTANT = 42
        self.reflection.getModule()._PROTECTED_CONSTANT = 24
        setattr(self.reflection.getModule(), "__PRIVATE_CONSTANT", 84)

        protected_constants = self.reflection.getProtectedConstants()
        self.assertNotIn("PUBLIC_CONSTANT", protected_constants)
        self.assertIn("_PROTECTED_CONSTANT", protected_constants)
        self.assertNotIn("__PRIVATE_CONSTANT", protected_constants)

    def testGetPrivateConstants(self):
        """
        Test getPrivateConstants method returns only private constants.

        Verifies that getPrivateConstants returns only constants that
        start with double underscore but don't end with double underscore.
        """
        # Add test constants with different visibility
        self.reflection.getModule().PUBLIC_CONSTANT = 42
        self.reflection.getModule()._PROTECTED_CONSTANT = 24
        setattr(self.reflection.getModule(), "__PRIVATE_CONSTANT", 84)

        private_constants = self.reflection.getPrivateConstants()
        self.assertNotIn("PUBLIC_CONSTANT", private_constants)
        self.assertNotIn("_PROTECTED_CONSTANT", private_constants)
        self.assertIn("__PRIVATE_CONSTANT", private_constants)

    def testGetFunctions(self):
        """
        Test getFunctions method returns dictionary of functions.

        Verifies that getFunctions returns a dictionary containing all
        callable objects with __code__ attribute (functions) in the module.
        """
        functions = self.reflection.getFunctions()
        self.assertIsInstance(functions, dict)
        # All values should be callable with __code__ attribute
        for func in functions.values():
            self.assertTrue(callable(func))
            self.assertTrue(hasattr(func, "__code__"))

    def testGetPublicFunctions(self):
        """
        Test getPublicFunctions method returns only public functions.

        Verifies that getPublicFunctions returns only functions that
        don't start with underscore.
        """
        # Add test functions with different visibility
        def public_function():
            # Empty function for testing public function visibility
            pass

        def _protected_function():
            # Empty function for testing protected function visibility
            pass

        def __private_function():
            # Empty function for testing private function visibility
            pass

        self.reflection.getModule().public_function = public_function
        self.reflection.getModule()._protected_function = _protected_function
        setattr(self.reflection.getModule(), "__private_function", __private_function)

        public_functions = self.reflection.getPublicFunctions()
        self.assertIn("public_function", public_functions)
        self.assertNotIn("_protected_function", public_functions)
        self.assertNotIn("__private_function", public_functions)

    def testGetPublicSyncFunctions(self):
        """
        Test getPublicSyncFunctions method returns only synchronous public functions.

        Verifies that getPublicSyncFunctions returns only public functions
        that are synchronous (not coroutines).
        """
        # Add test functions
        def sync_function():
            # Empty sync function for testing
            pass

        async def async_function():
            # Empty async function for testing
            pass

        self.reflection.getModule().sync_function = sync_function
        self.reflection.getModule().async_function = async_function

        sync_functions = self.reflection.getPublicSyncFunctions()
        self.assertIn("sync_function", sync_functions)
        self.assertNotIn("async_function", sync_functions)

    def testGetPublicAsyncFunctions(self):
        """
        Test getPublicAsyncFunctions method returns only asynchronous public functions.

        Verifies that getPublicAsyncFunctions returns only public functions
        that are asynchronous (coroutines).
        """
        # Add test functions
        def sync_function():
            # Empty sync function for testing
            pass

        async def async_function():
            # Empty async function for testing
            pass

        self.reflection.getModule().sync_function = sync_function
        self.reflection.getModule().async_function = async_function

        async_functions = self.reflection.getPublicAsyncFunctions()
        self.assertNotIn("sync_function", async_functions)
        self.assertIn("async_function", async_functions)

    def testGetProtectedFunctions(self):
        """
        Test getProtectedFunctions method returns only protected functions.

        Verifies that getProtectedFunctions returns only functions that
        start with single underscore.
        """
        # Add test functions with different visibility
        def public_function():
            # Empty function for testing public function visibility
            pass

        def _protected_function():
            # Empty function for testing protected function visibility
            pass

        def __private_function():
            # Empty function for testing private function visibility
            pass

        self.reflection.getModule().public_function = public_function
        self.reflection.getModule()._protected_function = _protected_function
        setattr(self.reflection.getModule(), "__private_function", __private_function)

        protected_functions = self.reflection.getProtectedFunctions()
        self.assertNotIn("public_function", protected_functions)
        self.assertIn("_protected_function", protected_functions)
        self.assertNotIn("__private_function", protected_functions)

    def testGetProtectedSyncFunctions(self):
        """
        Test getProtectedSyncFunctions method returns only synchronous protected functions.

        Verifies that getProtectedSyncFunctions returns only protected functions
        that are synchronous (not coroutines).
        """
        # Add test functions
        def _sync_protected():
            # Empty sync protected function for testing
            pass

        async def _async_protected():
            # Empty async protected function for testing
            pass

        self.reflection.getModule()._sync_protected = _sync_protected
        self.reflection.getModule()._async_protected = _async_protected

        sync_protected = self.reflection.getProtectedSyncFunctions()
        self.assertIn("_sync_protected", sync_protected)
        self.assertNotIn("_async_protected", sync_protected)

    def testGetProtectedAsyncFunctions(self):
        """
        Test getProtectedAsyncFunctions method returns only asynchronous protected functions.

        Verifies that getProtectedAsyncFunctions returns only protected functions
        that are asynchronous (coroutines).
        """
        # Add test functions
        def _sync_protected():
            # Empty sync protected function for testing
            pass

        async def _async_protected():
            # Empty async protected function for testing
            pass

        self.reflection.getModule()._sync_protected = _sync_protected
        self.reflection.getModule()._async_protected = _async_protected

        async_protected = self.reflection.getProtectedAsyncFunctions()
        self.assertNotIn("_sync_protected", async_protected)
        self.assertIn("_async_protected", async_protected)

    def testGetPrivateFunctions(self):
        """
        Test getPrivateFunctions method returns only private functions.

        Verifies that getPrivateFunctions returns only functions that
        start with double underscore but don't end with double underscore.
        """
        # Add test functions with different visibility
        def public_function():
            # Empty function for testing public function visibility
            pass

        def _protected_function():
            # Empty function for testing protected function visibility
            pass

        def __private_function():
            # Empty function for testing private function visibility
            pass

        self.reflection.getModule().public_function = public_function
        self.reflection.getModule()._protected_function = _protected_function
        setattr(self.reflection.getModule(), "__private_function", __private_function)

        private_functions = self.reflection.getPrivateFunctions()
        self.assertNotIn("public_function", private_functions)
        self.assertNotIn("_protected_function", private_functions)
        self.assertIn("__private_function", private_functions)

    def testGetPrivateSyncFunctions(self):
        """
        Test getPrivateSyncFunctions method returns only synchronous private functions.

        Verifies that getPrivateSyncFunctions returns only private functions
        that are synchronous (not coroutines).
        """
        # Add test functions
        def __sync_private():
            # Empty sync private function for testing
            pass

        async def __async_private():
            # Empty async private function for testing
            pass

        setattr(self.reflection.getModule(), "__sync_private", __sync_private)
        setattr(self.reflection.getModule(), "__async_private", __async_private)

        sync_private = self.reflection.getPrivateSyncFunctions()
        self.assertIn("__sync_private", sync_private)
        self.assertNotIn("__async_private", sync_private)

    def testGetPrivateAsyncFunctions(self):
        """
        Test getPrivateAsyncFunctions method returns only asynchronous private functions.

        Verifies that getPrivateAsyncFunctions returns only private functions
        that are asynchronous (coroutines).
        """
        # Add test functions
        def __sync_private():
            # Empty sync private function for testing
            pass

        async def __async_private():
            # Empty async private function for testing
            pass

        setattr(self.reflection.getModule(), "__sync_private", __sync_private)
        setattr(self.reflection.getModule(), "__async_private", __async_private)

        async_private = self.reflection.getPrivateAsyncFunctions()
        self.assertNotIn("__sync_private", async_private)
        self.assertIn("__async_private", async_private)

    def testGetImports(self):
        """
        Test getImports method returns dictionary of imported modules.

        Verifies that getImports returns a dictionary containing all
        imported module objects in the module.
        """
        imports = self.reflection.getImports()
        self.assertIsInstance(imports, dict)

    def testGetFile(self):
        """
        Test getFile method returns module file path.

        Verifies that getFile returns the correct file path for the
        imported module.
        """
        file_path = self.reflection.getFile()
        self.assertIsInstance(file_path, str)
        self.assertTrue(file_path.endswith(".py") or file_path.endswith(".pyc"))

    def testGetSourceCode(self):
        """
        Test getSourceCode method returns module source code.

        Verifies that getSourceCode returns the source code content
        of the module file.
        """
        with patch("builtins.open", mock_open(read_data='# Test source code\nprint("hello")')):
            source_code = self.reflection.getSourceCode()
            self.assertIsInstance(source_code, str)
            self.assertIn("# Test source code", source_code)

    def testGetSourceCodeWithFileError(self):
        """
        Test getSourceCode method with file reading error.

        Verifies that getSourceCode raises ReflectionValueError when
        unable to read the source file.

        Raises
        ------
        ReflectionValueError
            When the source file cannot be read.
        """
        with patch("builtins.open", side_effect=OSError("File not found")):
            with self.assertRaises(ReflectionValueError) as context:
                self.reflection.getSourceCode()
            self.assertIn("Failed to read source code", str(context.exception))

    def testEdgeCaseEmptyModule(self):
        """
        Test handling of an empty module.

        Verifies that the ReflectionModule correctly handles modules
        that have no classes, functions, or constants.
        """
        # Create a temporary empty module
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Empty module\n")
            temp_module_path = f.name

        try:
            # Add the temp file directory to sys.path temporarily
            temp_dir = os.path.dirname(temp_module_path)
            temp_module_name = os.path.basename(temp_module_path)[:-3]  # Remove .py extension

            if temp_dir not in sys.path:
                sys.path.insert(0, temp_dir)

            reflection = ReflectionModule(temp_module_name)
            self.assertEqual(len(reflection.getClasses()), 0)
            self.assertEqual(len(reflection.getFunctions()), 0)
            self.assertEqual(len(reflection.getConstants()), 0)

        finally:
            # Clean up
            if temp_dir in sys.path:
                sys.path.remove(temp_dir)
            os.unlink(temp_module_path)

    def testBuiltInModuleHandling(self):
        """
        Test handling of built-in modules.

        Verifies that ReflectionModule can work with built-in modules
        that may not have typical file paths.
        """
        reflection = ReflectionModule("sys")
        self.assertIsNotNone(reflection.getModule())
        # Built-in modules should still have classes and functions
        classes = reflection.getClasses()
        functions = reflection.getFunctions()
        self.assertIsInstance(classes, dict)
        self.assertIsInstance(functions, dict)
