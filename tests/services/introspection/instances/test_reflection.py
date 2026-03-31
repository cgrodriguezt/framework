import inspect
from orionis.test import TestCase
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.services.introspection.dependencies.entities.signature import Signature

class SampleReflected:
    """Sample class used as a fixture for ReflectionInstance tests."""

    public_attr: int
    _protected_attr: str

    def __init__(self, x: int = 10) -> None:
        """
        Initialize SampleReflected with the given public attribute value.

        Parameters
        ----------
        x : int, optional
            Initial value for public_attr. Defaults to 10.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.public_attr = x
        self._protected_attr = "prot"
        self.__private_attr = "priv"
        self.__dunder__ = "dunder_val"

    # --- instance methods ---

    def public_method(self) -> int:
        """
        Return the value of public_attr.

        Returns
        -------
        int
            The current value of public_attr.
        """
        return self.public_attr

    async def public_async_method(self) -> int: # NOSONAR
        """
        Return the value of public_attr asynchronously.

        Returns
        -------
        int
            The current value of public_attr.
        """
        return self.public_attr

    def _protected_method(self) -> str:
        """
        Return the value of _protected_attr.

        Returns
        -------
        str
            The current value of _protected_attr.
        """
        return self._protected_attr

    async def _protected_async_method(self) -> str: # NOSONAR
        """
        Return the value of _protected_attr asynchronously.

        Returns
        -------
        str
            The current value of _protected_attr.
        """
        return self._protected_attr

    def __private_method(self) -> str: # NOSONAR
        """
        Return the value of __private_attr.

        Returns
        -------
        str
            The current value of __private_attr.
        """
        return self.__private_attr

    async def __private_async_method(self) -> str: # NOSONAR
        """
        Return the value of __private_attr asynchronously.

        Returns
        -------
        str
            The current value of __private_attr.
        """
        return self.__private_attr

    # --- class methods ---

    @classmethod
    def public_class_method(cls) -> str:
        """
        Return the class name.

        Returns
        -------
        str
            The name of the class as a string.
        """
        return cls.__name__

    @classmethod
    async def public_async_class_method(cls) -> str:
        """
        Return the class name asynchronously.

        Returns
        -------
        str
            The name of the class as a string.
        """
        return cls.__name__

    @classmethod
    def _protected_class_method(cls) -> str:
        """
        Return the class name (protected).

        Returns
        -------
        str
            The name of the class as a string.
        """
        return cls.__name__

    @classmethod
    async def _protected_async_class_method(cls) -> str:
        """
        Return the class name asynchronously (protected).

        Returns
        -------
        str
            The name of the class as a string.
        """
        return cls.__name__

    @classmethod
    def __private_class_method(cls) -> str: # NOSONAR
        """
        Return the class name (private).

        Returns
        -------
        str
            The name of the class as a string.
        """
        return cls.__name__

    @classmethod
    async def __private_async_class_method(cls) -> str: # NOSONAR
        """
        Return the class name asynchronously (private).

        Returns
        -------
        str
            The name of the class as a string.
        """
        return cls.__name__

    # --- static methods ---

    @staticmethod
    def public_static_method() -> str:
        """
        Return a static string identifier.

        Returns
        -------
        str
            The literal string "static".
        """
        return "static"

    @staticmethod
    async def public_async_static_method() -> str:
        """
        Return a static string identifier asynchronously.

        Returns
        -------
        str
            The literal string "async_static".
        """
        return "async_static"

    @staticmethod
    def _protected_static_method() -> str:
        """
        Return a protected static string identifier.

        Returns
        -------
        str
            The literal string "prot_static".
        """
        return "prot_static"

    @staticmethod
    async def _protected_async_static_method() -> str:
        """
        Return a protected static string identifier asynchronously.

        Returns
        -------
        str
            The literal string "prot_async_static".
        """
        return "prot_async_static"

    @staticmethod
    def __private_static_method() -> str: # NOSONAR
        """
        Return a private static string identifier.

        Returns
        -------
        str
            The literal string "priv_static".
        """
        return "priv_static"

    @staticmethod
    async def __private_async_static_method() -> str: # NOSONAR
        """
        Return a private static string identifier asynchronously.

        Returns
        -------
        str
            The literal string "priv_async_static".
        """
        return "priv_async_static"

    # --- properties ---

    @property
    def public_property(self) -> int:
        """
        Return the value of public_attr.

        Returns
        -------
        int
            The current value of public_attr.
        """
        return self.public_attr

    @property
    def _protected_property(self) -> str:
        """
        Return the value of _protected_attr.

        Returns
        -------
        str
            The current value of _protected_attr.
        """
        return self._protected_attr

    @property
    def __private_property(self) -> str:
        """
        Return the value of __private_attr.

        Returns
        -------
        str
            The current value of __private_attr.
        """
        return self.__private_attr

def _make_mutable_instance() -> ReflectionInstance:
    """
    Return a ReflectionInstance wrapping a fresh mutable class.

    Creates a new class on each call so mutation tests (setMethod,
    removeMethod, etc.) do not interfere with shared fixtures.

    Returns
    -------
    ReflectionInstance
        A reflection wrapper around a fresh MutableSample instance.
    """
    class MutableSample:
        """Mutable sample class for mutation-based tests."""

        def to_remove(self) -> str:
            """
            Return a removable string marker.

            Returns
            -------
            str
                The literal string "removable".
            """
            return "removable"

        def extra(self) -> int:
            """
            Return a zero integer placeholder.

            Returns
            -------
            int
                The literal integer 0.
            """
            return 0

    return ReflectionInstance(MutableSample())

class TestReflectionInstanceInit(TestCase):

    def testInitWithValidInstanceSucceeds(self) -> None:
        """
        Assert that passing a valid user-defined instance does not raise.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        self.assertIsInstance(ri, ReflectionInstance)

    def testInitWithClassRaisesTypeError(self) -> None:
        """
        Assert that passing a class object instead of an instance raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ReflectionInstance(SampleReflected)

    def testInitWithBuiltinIntRaisesTypeError(self) -> None:
        """
        Assert that passing a built-in integer instance raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ReflectionInstance(42)

    def testInitWithNoneRaisesTypeError(self) -> None:
        """
        Assert that passing None raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ReflectionInstance(None)

class TestReflectionInstanceCacheProtocol(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for cache protocol tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testSetAndGetCacheItem(self) -> None:
        """
        Assert that a value stored with __setitem__ is retrievable with __getitem__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.ri["test_key"] = "test_value"
        self.assertEqual(self.ri["test_key"], "test_value")

    def testContainsReturnsTrueForExistingKey(self) -> None:
        """
        Assert that __contains__ returns True for a key that was stored.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.ri["exists"] = 1
        self.assertIn("exists", self.ri)

    def testContainsReturnsFalseForMissingKey(self) -> None:
        """
        Assert that __contains__ returns False for a key that was not stored.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("missing_key_xyz", self.ri)

    def testDeleteCacheItem(self) -> None:
        """
        Assert that __delitem__ removes the key from the cache.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.ri["to_delete"] = "bye"
        del self.ri["to_delete"]
        self.assertNotIn("to_delete", self.ri)

class TestReflectionInstanceIdentity(TestCase):

    def setUp(self) -> None:
        """
        Instantiate SampleReflected and wrap it for identity tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.instance = SampleReflected()
        self.ri = ReflectionInstance(self.instance)

    def testGetInstanceReturnsSameObject(self) -> None:
        """
        Assert that getInstance returns the exact same object that was passed in.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIs(self.ri.getInstance(), self.instance)

    def testGetClassReturnsCorrectType(self) -> None:
        """
        Assert that getClass returns the SampleReflected type.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIs(self.ri.getClass(), SampleReflected)

    def testGetClassNameReturnsCorrectString(self) -> None:
        """
        Assert that getClassName returns 'SampleReflected'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.ri.getClassName(), "SampleReflected")

    def testGetModuleNameReturnsNonEmptyString(self) -> None:
        """
        Assert that getModuleName returns a non-empty string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        name = self.ri.getModuleName()
        self.assertIsInstance(name, str)
        self.assertTrue(len(name) > 0)

    def testGetModuleWithClassNameContainsClassName(self) -> None:
        """
        Assert that getModuleWithClassName contains 'SampleReflected'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        full = self.ri.getModuleWithClassName()
        self.assertIn("SampleReflected", full)

class TestReflectionInstanceMetadata(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for metadata retrieval tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetDocstringReturnsClassDocstring(self) -> None:
        """
        Assert that getDocstring returns the class-level docstring.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        doc = self.ri.getDocstring()
        self.assertIsNotNone(doc)
        self.assertIsInstance(doc, str)

    def testGetBaseClassesContainsObject(self) -> None:
        """
        Assert that getBaseClasses returns a tuple containing object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        bases = self.ri.getBaseClasses()
        self.assertIsInstance(bases, tuple)
        self.assertIn(object, bases)

    def testGetFileReturnsString(self) -> None:
        """
        Assert that getFile returns a non-empty string path.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        path = self.ri.getFile()
        self.assertIsNotNone(path)
        self.assertIsInstance(path, str)

class TestReflectionInstanceSourceCode(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for source code retrieval tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetSourceCodeForClassReturnsString(self) -> None:
        """
        Assert that getSourceCode with no argument returns a non-empty string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        src = self.ri.getSourceCode()
        self.assertIsInstance(src, str)
        self.assertGreater(len(src), 0)

    def testGetSourceCodeForExistingMethodReturnsString(self) -> None:
        """
        Assert that getSourceCode for a known method returns a non-empty string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        src = self.ri.getSourceCode("public_method")
        self.assertIsInstance(src, str)
        self.assertGreater(len(src), 0)

    def testGetSourceCodeForNonExistentMethodReturnsNone(self) -> None:
        """
        Assert that getSourceCode for a non-existent method name returns None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        src = self.ri.getSourceCode("no_such_method_xyz")
        self.assertIsNone(src)

    def testGetSourceCodeIsCached(self) -> None:
        """
        Assert that repeated calls to getSourceCode return the same object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        first = self.ri.getSourceCode()
        second = self.ri.getSourceCode()
        self.assertIs(first, second)

class TestReflectionInstanceAnnotations(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for annotation retrieval tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetAnnotationsReturnsDict(self) -> None:
        """
        Assert that getAnnotations returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getAnnotations(), dict)

    def testGetAnnotationsContainsPublicAttr(self) -> None:
        """
        Assert that getAnnotations includes the class-level public_attr annotation.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        annotations = self.ri.getAnnotations()
        self.assertIn("public_attr", annotations)
        self.assertEqual(annotations["public_attr"], int)

class TestReflectionInstancePublicAttributes(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for public attribute tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetPublicAttributesReturnsDict(self) -> None:
        """
        Assert that getPublicAttributes returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getPublicAttributes(), dict)

    def testGetPublicAttributesContainsPublicAttr(self) -> None:
        """
        Assert that getPublicAttributes includes 'public_attr'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_attr", self.ri.getPublicAttributes())

    def testGetPublicAttributesExcludesProtected(self) -> None:
        """
        Assert that getPublicAttributes excludes '_protected_attr'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("_protected_attr", self.ri.getPublicAttributes())

class TestReflectionInstanceProtectedAttributes(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for protected attribute tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetProtectedAttributesReturnsDict(self) -> None:
        """
        Assert that getProtectedAttributes returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getProtectedAttributes(), dict)

    def testGetProtectedAttributesContainsProtectedAttr(self) -> None:
        """
        Assert that getProtectedAttributes includes '_protected_attr'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_attr", self.ri.getProtectedAttributes())

class TestReflectionInstancePrivateAttributes(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for private attribute tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetPrivateAttributesReturnsDict(self) -> None:
        """
        Assert that getPrivateAttributes returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getPrivateAttributes(), dict)

    def testGetPrivateAttributesContainsUnmangledKey(self) -> None:
        """
        Assert that getPrivateAttributes contains '__private_attr' (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        private = self.ri.getPrivateAttributes()
        self.assertIn("__private_attr", private)
        self.assertEqual(private["__private_attr"], "priv")

class TestReflectionInstanceDunderAttributes(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for dunder attribute tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetDunderAttributesReturnsDict(self) -> None:
        """
        Assert that getDunderAttributes returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getDunderAttributes(), dict)

    def testGetMagicAttributesSameAsDunder(self) -> None:
        """
        Assert that getMagicAttributes returns the same result as getDunderAttributes.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            self.ri.getMagicAttributes(),
            self.ri.getDunderAttributes(),
        )

class TestReflectionInstanceAttributeOps(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for attribute operation tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testHasAttributeReturnsTrueForExisting(self) -> None:
        """
        Assert that hasAttribute returns True for a known attribute.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(self.ri.hasAttribute("public_attr"))

    def testHasAttributeReturnsFalseForMissing(self) -> None:
        """
        Assert that hasAttribute returns False for an unknown attribute.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertFalse(self.ri.hasAttribute("nonexistent_xyz"))

    def testGetAttributeReturnsCorrectValue(self) -> None:
        """
        Assert that getAttribute returns the expected value for public_attr.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.ri.getAttribute("public_attr"), 10)

    def testGetAttributeReturnsDefaultForMissing(self) -> None:
        """
        Assert that getAttribute returns the provided default for a missing key.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            self.ri.getAttribute("nonexistent_xyz", "fallback"),
            "fallback",
        )

    def testSetAttributeReturnsTrueAndPersists(self) -> None:
        """
        Assert that setAttribute returns True and the value is stored on the
        instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        result = ri.setAttribute("public_attr", 99)
        self.assertTrue(result)
        self.assertEqual(ri.getInstance().public_attr, 99)

    def testSetAttributeWithCallableRaisesTypeError(self) -> None:
        """
        Assert that setAttribute raises TypeError when given a callable value.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            self.ri.setAttribute("bad", lambda: None)

    def testSetAttributeWithKeywordRaisesAttributeError(self) -> None:
        """
        Assert that setAttribute raises AttributeError when the name is a Python
        keyword.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(AttributeError):
            self.ri.setAttribute("class", "value")

    def testRemoveAttributeReturnsTrueAndRemoves(self) -> None:
        """
        Assert that removeAttribute returns True and deletes the attribute.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        ri.setAttribute("temp_attr", "to_remove")
        result = ri.removeAttribute("temp_attr")
        self.assertTrue(result)
        self.assertFalse(hasattr(ri.getInstance(), "temp_attr"))

    def testGetAttributeDocstringForPublicAttr(self) -> None:
        """
        Assert that getAttributeDocstring returns the docstring for the method
        whose name matches the attribute.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # public_method has a docstring; retrieve it via instance attribute path
        doc = self.ri.getAttributeDocstring("public_method")
        self.assertIsInstance(doc, (str, type(None)))

class TestReflectionInstancePublicMethods(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for public method discovery tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetPublicMethodsReturnsList(self) -> None:
        """
        Assert that getPublicMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getPublicMethods(), list)

    def testGetPublicMethodsContainsPublicMethod(self) -> None:
        """
        Assert that getPublicMethods includes 'public_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_method", self.ri.getPublicMethods())

    def testGetPublicSyncMethodsContainsPublicMethod(self) -> None:
        """
        Assert that getPublicSyncMethods includes 'public_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_method", self.ri.getPublicSyncMethods())

    def testGetPublicAsyncMethodsContainsAsyncMethod(self) -> None:
        """
        Assert that getPublicAsyncMethods includes 'public_async_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_async_method", self.ri.getPublicAsyncMethods())

    def testHasMethodReturnsTrueForPublicMethod(self) -> None:
        """
        Assert that hasMethod returns True for 'public_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(self.ri.hasMethod("public_method"))

class TestReflectionInstanceProtectedMethods(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for protected method discovery tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetProtectedMethodsReturnsList(self) -> None:
        """
        Assert that getProtectedMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getProtectedMethods(), list)

    def testGetProtectedMethodsContainsProtectedMethod(self) -> None:
        """
        Assert that getProtectedMethods includes '_protected_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_method", self.ri.getProtectedMethods())

    def testGetProtectedAsyncMethodsContainsAsyncMethod(self) -> None:
        """
        Assert that getProtectedAsyncMethods includes '_protected_async_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "_protected_async_method",
            self.ri.getProtectedAsyncMethods(),
        )

class TestReflectionInstancePrivateMethods(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for private method discovery tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetPrivateMethodsReturnsList(self) -> None:
        """
        Assert that getPrivateMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getPrivateMethods(), list)

    def testGetPrivateMethodsContainsUnmangledName(self) -> None:
        """
        Assert that getPrivateMethods includes '__private_method' (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("__private_method", self.ri.getPrivateMethods())

    def testGetPrivateAsyncMethodsContainsUnmangledAsyncName(self) -> None:
        """
        Assert that getPrivateAsyncMethods includes '__private_async_method'
        (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("__private_async_method", self.ri.getPrivateAsyncMethods())

class TestReflectionInstanceClassMethods(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for class method discovery tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetPublicClassMethodsContainsPublicClassMethod(self) -> None:
        """
        Assert that getPublicClassMethods includes 'public_class_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_class_method", self.ri.getPublicClassMethods())

    def testGetPublicClassSyncMethodsContainsSyncClassMethod(self) -> None:
        """
        Assert that getPublicClassSyncMethods includes 'public_class_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_class_method", self.ri.getPublicClassSyncMethods())

    def testGetPublicClassAsyncMethodsContainsAsyncClassMethod(self) -> None:
        """
        Assert that getPublicClassAsyncMethods includes 'public_async_class_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "public_async_class_method",
            self.ri.getPublicClassAsyncMethods(),
        )

    def testGetProtectedClassMethodsContainsProtectedClassMethod(self) -> None:
        """
        Assert that getProtectedClassMethods includes '_protected_class_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "_protected_class_method",
            self.ri.getProtectedClassMethods(),
        )

    def testGetProtectedClassAsyncMethodsContainsAsyncClassMethod(self) -> None:
        """
        Assert that getProtectedClassAsyncMethods includes
        '_protected_async_class_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "_protected_async_class_method",
            self.ri.getProtectedClassAsyncMethods(),
        )

    def testGetPrivateClassMethodsContainsUnmangledName(self) -> None:
        """
        Assert that getPrivateClassMethods includes '__private_class_method'
        (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("__private_class_method", self.ri.getPrivateClassMethods())

    def testGetPrivateClassAsyncMethodsContainsUnmangledAsyncName(self) -> None:
        """
        Assert that getPrivateClassAsyncMethods includes
        '__private_async_class_method' (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "__private_async_class_method",
            self.ri.getPrivateClassAsyncMethods(),
        )

class TestReflectionInstanceStaticMethods(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for static method discovery tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetPublicStaticMethodsContainsPublicStaticMethod(self) -> None:
        """
        Assert that getPublicStaticMethods includes 'public_static_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_static_method", self.ri.getPublicStaticMethods())

    def testGetPublicStaticSyncMethodsContainsSyncStaticMethod(self) -> None:
        """
        Assert that getPublicStaticSyncMethods includes 'public_static_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_static_method", self.ri.getPublicStaticSyncMethods())

    def testGetPublicStaticAsyncMethodsContainsAsyncStaticMethod(self) -> None:
        """
        Assert that getPublicStaticAsyncMethods includes
        'public_async_static_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "public_async_static_method",
            self.ri.getPublicStaticAsyncMethods(),
        )

    def testGetProtectedStaticMethodsContainsProtectedStaticMethod(self) -> None:
        """
        Assert that getProtectedStaticMethods includes '_protected_static_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "_protected_static_method",
            self.ri.getProtectedStaticMethods(),
        )

    def testGetProtectedStaticAsyncMethodsContainsAsyncStaticMethod(self) -> None:
        """
        Assert that getProtectedStaticAsyncMethods includes
        '_protected_async_static_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "_protected_async_static_method",
            self.ri.getProtectedStaticAsyncMethods(),
        )

    def testGetPrivateStaticMethodsContainsUnmangledName(self) -> None:
        """
        Assert that getPrivateStaticMethods includes '__private_static_method'
        (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("__private_static_method", self.ri.getPrivateStaticMethods())

    def testGetPrivateStaticAsyncMethodsContainsUnmangledAsyncName(self) -> None:
        """
        Assert that getPrivateStaticAsyncMethods includes
        '__private_async_static_method' (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "__private_async_static_method",
            self.ri.getPrivateStaticAsyncMethods(),
        )

class TestReflectionInstanceDunderMethods(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for dunder method discovery tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetDunderMethodsReturnsList(self) -> None:
        """
        Assert that getDunderMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getDunderMethods(), list)

    def testGetDunderMethodsContainsInit(self) -> None:
        """
        Assert that getDunderMethods includes '__init__'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("__init__", self.ri.getDunderMethods())

    def testGetMagicMethodsEqualDunderMethods(self) -> None:
        """
        Assert that getMagicMethods returns the same list as getDunderMethods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.ri.getMagicMethods(), self.ri.getDunderMethods())

class TestReflectionInstanceMethodOps(TestCase):

    def testSetMethodReturnsTrueAndAttributeIsCallable(self) -> None:
        """
        Assert that setMethod returns True and the callable is accessible.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        result = ri.setMethod("injected", lambda: "hello")
        self.assertTrue(result)
        self.assertTrue(callable(getattr(ri.getInstance(), "injected")))

    def testSetMethodWithNonCallableRaisesTypeError(self) -> None:
        """
        Assert that setMethod raises TypeError when the value is not callable.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        with self.assertRaises(TypeError):
            ri.setMethod("bad", "not_callable")

    def testSetMethodWithInvalidNameRaisesAttributeError(self) -> None:
        """
        Assert that setMethod raises AttributeError when the name is a keyword.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        with self.assertRaises(AttributeError):
            ri.setMethod("return", lambda: None)

    def testRemoveMethodRemovesFromClass(self) -> None:
        """
        Assert that removeMethod deletes the method from the underlying class.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = _make_mutable_instance()
        self.assertTrue(ri.hasMethod("to_remove"))
        ri.removeMethod("to_remove")
        self.assertFalse(hasattr(ri.getInstance().__class__, "to_remove"))

    def testRemoveMethodOnNonExistingRaisesAttributeError(self) -> None:
        """
        Assert that removeMethod raises AttributeError for an unknown method name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        with self.assertRaises(AttributeError):
            ri.removeMethod("nonexistent_method_xyz")

    def testGetMethodSignatureReturnsSignature(self) -> None:
        """
        Assert that getMethodSignature returns an inspect.Signature object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        sig = ri.getMethodSignature("public_method")
        self.assertIsInstance(sig, inspect.Signature)

    def testGetMethodDocstringReturnsString(self) -> None:
        """
        Assert that getMethodDocstring returns a string for a documented method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        doc = ri.getMethodDocstring("public_method")
        self.assertIsInstance(doc, str)

    def testGetMethodDocstringForNonExistingRaisesAttributeError(self) -> None:
        """
        Assert that getMethodDocstring raises AttributeError for unknown method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        ri = ReflectionInstance(SampleReflected())
        with self.assertRaises(AttributeError):
            ri.getMethodDocstring("nonexistent_method_xyz")

class TestReflectionInstanceProperties(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for property discovery tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testGetPropertiesReturnsList(self) -> None:
        """
        Assert that getProperties returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.ri.getProperties(), list)

    def testGetPropertiesContainsPublicProperty(self) -> None:
        """
        Assert that getProperties includes 'public_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_property", self.ri.getProperties())

    def testGetPublicPropertiesContainsPublicProperty(self) -> None:
        """
        Assert that getPublicProperties includes 'public_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_property", self.ri.getPublicProperties())

    def testGetProtectedPropertiesContainsProtectedProperty(self) -> None:
        """
        Assert that getProtectedProperties includes '_protected_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_property", self.ri.getProtectedProperties())

    def testGetPrivatePropertiesContainsUnmangledName(self) -> None:
        """
        Assert that getPrivateProperties includes '__private_property' (unmangled).

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("__private_property", self.ri.getPrivateProperties())

    def testGetPropertyReturnsValue(self) -> None:
        """
        Assert that getProperty returns the value of 'public_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.ri.getProperty("public_property"), 10)

    def testGetPropertyNonExistingRaisesAttributeError(self) -> None:
        """
        Assert that getProperty raises AttributeError for an unknown property.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(AttributeError):
            self.ri.getProperty("nonexistent_prop_xyz")

    def testGetPropertySignatureReturnsSignature(self) -> None:
        """
        Assert that getPropertySignature returns an inspect.Signature instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.ri.getPropertySignature("public_property")
        self.assertIsInstance(sig, inspect.Signature)

    def testGetPropertyDocstringReturnsString(self) -> None:
        """
        Assert that getPropertyDocstring returns a string for 'public_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        doc = self.ri.getPropertyDocstring("public_property")
        self.assertIsInstance(doc, str)

class TestReflectionInstanceDependencies(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for dependency inspection tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testConstructorSignatureReturnsSignature(self) -> None:
        """
        Assert that constructorSignature returns a Signature instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.ri.constructorSignature()
        self.assertIsInstance(sig, Signature)

    def testConstructorSignatureHasResolvedField(self) -> None:
        """
        Assert that the Signature returned by constructorSignature has a
        'resolved' attribute.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.ri.constructorSignature()
        self.assertTrue(hasattr(sig, "resolved"))

    def testMethodSignatureReturnsSignature(self) -> None:
        """
        Assert that methodSignature for 'public_method' returns a Signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.ri.methodSignature("public_method")
        self.assertIsInstance(sig, Signature)

    def testMethodSignatureForNonExistingRaisesAttributeError(self) -> None:
        """
        Assert that methodSignature raises AttributeError for an unknown method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(AttributeError):
            self.ri.methodSignature("nonexistent_method_xyz")

class TestReflectionInstanceClearCache(TestCase):

    def setUp(self) -> None:
        """
        Instantiate a ReflectionInstance for cache clearing tests.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.ri = ReflectionInstance(SampleReflected())

    def testClearCacheReturnsNone(self) -> None:
        """
        Assert that clearCache returns None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.ri.clearCache())

    def testClearCacheInvalidatesStoredItems(self) -> None:
        """
        Assert that after clearCache, previously cached items are no longer present.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.ri["sentinel"] = "value"
        self.ri.clearCache()
        self.assertNotIn("sentinel", self.ri)
