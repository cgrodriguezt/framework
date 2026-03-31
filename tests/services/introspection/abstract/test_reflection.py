import inspect
from abc import ABC, abstractmethod
from orionis.test import TestCase
from orionis.services.introspection.abstract.reflection import ReflectionAbstract

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

class SampleABC(ABC):
    """Fixture ABC with a variety of members for introspection testing."""

    public_attr: int = 10
    _protected_attr: str = "protected"
    __private_attr: str = "private" # NOSONAR

    @abstractmethod
    def abstract_method(self) -> str:
        """Return an unimplemented abstract result."""

    def concrete_method(self) -> int:
        """
        Return a fixed integer.

        Returns
        -------
        int
            Always returns 42.
        """
        return 42

    async def async_method(self) -> str: # NOSONAR
        """
        Return a fixed async string.

        Returns
        -------
        str
            Always returns 'async_result'.
        """
        return "async_result"

    def _protected_method(self) -> bool:
        """
        Return a fixed boolean.

        Returns
        -------
        bool
            Always returns True.
        """
        return True

    async def _protected_async_method(self) -> None:
        """
        Execute an async no-op.

        Returns
        -------
        None
            This coroutine has no return value.
        """

    def __private_method(self) -> str: # NOSONAR
        """
        Return a fixed private string.

        Returns
        -------
        str
            Always returns 'private'.
        """
        return "private"

    @staticmethod
    def static_method() -> bool:
        """
        Return a fixed boolean from a static context.

        Returns
        -------
        bool
            Always returns True.
        """
        return True

    @staticmethod
    def _protected_static_method() -> int:
        """
        Return a fixed integer from a protected static context.

        Returns
        -------
        int
            Always returns 0.
        """
        return 0

    @classmethod
    def class_method(cls) -> str:
        """
        Return the name of the calling class.

        Returns
        -------
        str
            The __name__ of the class on which this is called.
        """
        return cls.__name__

    @classmethod
    def _protected_class_method(cls) -> None:
        """
        Execute a protected class-level no-op.

        Returns
        -------
        None
            This method has no return value.
        """

    @property
    def a_property(self) -> int:
        """
        Return a fixed integer from a public property.

        Returns
        -------
        int
            Always returns 0.
        """
        return 0

    @property
    def _protected_property(self) -> str:
        """
        Return a fixed string from a protected property.

        Returns
        -------
        str
            Always returns 'protected_value'.
        """
        return "protected_value"

class _NoDocABC(ABC):
    """Provide an ABC intentionally without a runtime class docstring."""

    @abstractmethod
    def method(self) -> None: ...

class _ConcreteClass:
    """Represent an ordinary non-abstract class fixture."""
    pass

def _make_mutable_abc() -> type:
    """
    Return a fresh ABC type whose attributes/methods can be deleted.

    Returns
    -------
    type
        A new ABC subclass with a mutable_attr and a deletable_method.

    Notes
    -----
    Calling this function every time ensures test isolation: each test
    that mutates the class starts with a clean, independent type.
    """
    class _MutableABC(ABC):
        mutable_attr: int = 99

        @abstractmethod
        def abstract_method(self) -> str: ...

        def deletable_method(self) -> int:
            """
            Return a fixed integer.

            Returns
            -------
            int
                Always returns 1.
            """
            return 1

    return _MutableABC

# ---------------------------------------------------------------------------
# __init__ behaviour
# ---------------------------------------------------------------------------

class TestReflectionAbstractInit(TestCase):

    def testInitWithAbstractClassSucceeds(self) -> None:
        """
        Assert that a valid ABC constructs ReflectionAbstract without error.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        SampleABC is abstract because abstract_method is not implemented.
        """
        r = ReflectionAbstract(SampleABC)
        self.assertIsNotNone(r)

    def testInitWithConcreteClassRaisesTypeError(self) -> None:
        """
        Assert that passing a non-abstract class raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        _ConcreteClass has no @abstractmethod declarations.
        """
        with self.assertRaises(TypeError):
            ReflectionAbstract(_ConcreteClass)

    def testInitWithBuiltinNonAbstractRaisesTypeError(self) -> None:
        """
        Assert that a plain built-in type raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ReflectionAbstract(int)

    def testInitWithNonTypeRaisesError(self) -> None:
        """
        Assert that passing a non-type raises TypeError or AttributeError.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        inspect.isabstract raises AttributeError for non-type objects when
        accessing __abstractmethods__.
        """
        with self.assertRaises((TypeError, AttributeError)):
            ReflectionAbstract("not_a_class")

    def testInstanceIsReflectionAbstract(self) -> None:
        """
        Assert that the created object is a ReflectionAbstract instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        r = ReflectionAbstract(SampleABC)
        self.assertIsInstance(r, ReflectionAbstract)

# ---------------------------------------------------------------------------
# Internal cache protocol (__getitem__, __setitem__, __contains__, __delitem__)
# ---------------------------------------------------------------------------

class TestReflectionAbstractCacheProtocol(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract instance for cache tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testSetAndGetItem(self) -> None:
        """
        Assert that a value stored via __setitem__ is returned by __getitem__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.r["my_key"] = "my_value"
        self.assertEqual(self.r["my_key"], "my_value")

    def testContainsTrueForStoredKey(self) -> None:
        """
        Assert that __contains__ returns True for an existing cache entry.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.r["cache_hit"] = 42
        self.assertIn("cache_hit", self.r)

    def testContainsFalseForMissingKey(self) -> None:
        """
        Assert that __contains__ returns False for an unknown key.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("no_such_key", self.r)

    def testGetItemReturnsNoneForMissingKey(self) -> None:
        """
        Assert that __getitem__ returns None for an absent key.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.r["ghost_key"])

    def testDelItemRemovesKey(self) -> None:
        """
        Assert that __delitem__ removes a previously stored entry.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.r["to_delete"] = "value"
        del self.r["to_delete"]
        self.assertNotIn("to_delete", self.r)

    def testDelItemOnMissingKeyNoError(self) -> None:
        """
        Assert that __delitem__ on a missing key does not raise.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        del self.r["nonexistent"]

# ---------------------------------------------------------------------------
# Identity methods
# ---------------------------------------------------------------------------

class TestReflectionAbstractIdentity(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract instance for identity tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetClassReturnsSampleABC(self) -> None:
        """
        Assert that getClass returns the exact type passed to the constructor.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIs(self.r.getClass(), SampleABC)

    def testGetClassNameReturnsStr(self) -> None:
        """
        Assert that getClassName returns a str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getClassName(), str)

    def testGetClassNameValue(self) -> None:
        """
        Assert that getClassName equals SampleABC.__name__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.r.getClassName(), "SampleABC")

    def testGetModuleNameReturnsStr(self) -> None:
        """
        Assert that getModuleName returns a non-empty str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getModuleName()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def testGetModuleWithClassNameContainsClassName(self) -> None:
        """
        Assert that getModuleWithClassName includes the class name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        fqn = self.r.getModuleWithClassName()
        self.assertIn("SampleABC", fqn)

    def testGetModuleWithClassNameContainsModuleName(self) -> None:
        """
        Assert that getModuleWithClassName includes the module name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        fqn = self.r.getModuleWithClassName()
        self.assertIn(self.r.getModuleName(), fqn)

# ---------------------------------------------------------------------------
# Metadata methods
# ---------------------------------------------------------------------------

class TestReflectionAbstractMetadata(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract instance for metadata tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetDocstringReturnsStr(self) -> None:
        """
        Assert that getDocstring returns a str when a docstring is defined.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getDocstring()
        self.assertIsInstance(result, str)

    def testGetDocstringNoneWhenAbsent(self) -> None:
        """
        Assert that getDocstring returns None when __doc__ is None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        class _Bare(ABC):
            @abstractmethod
            def m(self): ...

        # Force __doc__ to None to simulate a class with no docstring
        _Bare.__doc__ = None
        r = ReflectionAbstract(_Bare)
        self.assertIsNone(r.getDocstring())

    def testGetBaseClassesReturnsList(self) -> None:
        """
        Assert that getBaseClasses returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getBaseClasses(), list)

    def testGetBaseClassesContainsABC(self) -> None:
        """
        Assert that ABC appears in the base classes of SampleABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(ABC, self.r.getBaseClasses())

    def testGetSourceCodeReturnsStr(self) -> None:
        """
        Assert that getSourceCode returns a non-empty str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getSourceCode()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def testGetFileReturnsStr(self) -> None:
        """
        Assert that getFile returns a path string ending with '.py'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getFile()
        self.assertIsInstance(result, str)
        self.assertTrue(result.endswith(".py"))

    def testGetAnnotationsReturnsDict(self) -> None:
        """
        Assert that getAnnotations returns a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getAnnotations(), dict)

    def testGetAnnotationsContainsPublicAttr(self) -> None:
        """
        Assert that 'public_attr' appears in the normalised annotations.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        annotations = self.r.getAnnotations()
        self.assertIn("public_attr", annotations)

# ---------------------------------------------------------------------------
# Attribute inspection
# ---------------------------------------------------------------------------

class TestReflectionAbstractPublicAttributes(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for public attribute tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetPublicAttributesReturnsDict(self) -> None:
        """
        Assert that getPublicAttributes returns a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPublicAttributes(), dict)

    def testPublicAttrPresentInPublicAttributes(self) -> None:
        """
        Assert that 'public_attr' appears in the public attributes dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_attr", self.r.getPublicAttributes())

    def testProtectedAttrNotInPublicAttributes(self) -> None:
        """
        Assert that '_protected_attr' is absent from the public attributes dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("_protected_attr", self.r.getPublicAttributes())

    def testHasAttributeReturnsTrueForPublicAttr(self) -> None:
        """
        Assert that hasAttribute returns True for the known 'public_attr'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(self.r.hasAttribute("public_attr"))

    def testHasAttributeReturnsFalseForUnknown(self) -> None:
        """
        Assert that hasAttribute returns False for an absent name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertFalse(self.r.hasAttribute("nonexistent_attr"))

    def testGetAttributeReturnsValue(self) -> None:
        """
        Assert that getAttribute returns 10 for 'public_attr'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.r.getAttribute("public_attr"), 10)

    def testGetAttributeReturnsNoneForMissing(self) -> None:
        """
        Assert that getAttribute returns None for an absent name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.r.getAttribute("does_not_exist"))

    def testGetAttributesReturnsDict(self) -> None:
        """
        Assert that getAttributes returns an aggregated dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getAttributes(), dict)

class TestReflectionAbstractProtectedAttributes(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for protected attribute tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetProtectedAttributesReturnsDict(self) -> None:
        """
        Assert that getProtectedAttributes returns a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getProtectedAttributes(), dict)

    def testProtectedAttrPresent(self) -> None:
        """
        Assert that '_protected_attr' is listed in protected attributes.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_attr", self.r.getProtectedAttributes())

    def testPublicAttrNotInProtectedAttributes(self) -> None:
        """
        Assert that 'public_attr' is absent from the protected attributes dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("public_attr", self.r.getProtectedAttributes())

class TestReflectionAbstractPrivateAttributes(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for private attribute tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetPrivateAttributesReturnsDict(self) -> None:
        """
        Assert that getPrivateAttributes returns a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPrivateAttributes(), dict)

    def testPrivateAttrPresentWithStrippedName(self) -> None:
        """
        Assert that the mangled attr is returned as '__private_attr'.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        Python mangles __private_attr in SampleABC to _SampleABC__private_attr.
        ReflectionAbstract strips the '_SampleABC' prefix.
        """
        private_attrs = self.r.getPrivateAttributes()
        self.assertIn("__private_attr", private_attrs)

class TestReflectionAbstractDunderAttributes(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for dunder attribute tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetDunderAttributesReturnsDict(self) -> None:
        """
        Assert that getDunderAttributes returns a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getDunderAttributes(), dict)

    def testGetMagicAttributesDelegatesToDunder(self) -> None:
        """
        Assert that getMagicAttributes returns the same result as getDunderAttributes.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            self.r.getMagicAttributes(),
            self.r.getDunderAttributes(),
        )

# ---------------------------------------------------------------------------
# Attribute mutation
# ---------------------------------------------------------------------------

class TestReflectionAbstractSetAttribute(TestCase):

    def testSetAttributeAddsNewAttribute(self) -> None:
        """
        Assert that setAttribute returns True and the attribute becomes visible.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        MutableABC = _make_mutable_abc()
        r = ReflectionAbstract(MutableABC)
        result = r.setAttribute("new_attr", 123)
        self.assertTrue(result)
        # Verify visibility either via hasAttribute or direct hasattr
        self.assertTrue(
            r.hasAttribute("new_attr") or hasattr(MutableABC, "new_attr")
        )

    def testSetAttributeInvalidNameRaisesValueError(self) -> None:
        """
        Assert that an invalid identifier name raises ValueError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        r = ReflectionAbstract(SampleABC)
        with self.assertRaises(ValueError):
            r.setAttribute("1bad_name", 1)

    def testSetAttributeKeywordNameRaisesValueError(self) -> None:
        """
        Assert that a Python keyword as attribute name raises ValueError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        r = ReflectionAbstract(SampleABC)
        with self.assertRaises(ValueError):
            r.setAttribute("class", 1)

    def testSetAttributeCallableValueRaisesTypeError(self) -> None:
        """
        Assert that passing a callable value raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        The implementation distinguishes invalid names (ValueError) from
        callable values (TypeError) as separate error categories.
        """
        r = ReflectionAbstract(SampleABC)
        with self.assertRaises(TypeError):
            r.setAttribute("new_method", lambda: None)

class TestReflectionAbstractRemoveAttribute(TestCase):

    def testRemoveAttributeReturnsTrueOnSuccess(self) -> None:
        """
        Assert that removeAttribute returns True and the attribute is gone.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        MutableABC = _make_mutable_abc()
        r = ReflectionAbstract(MutableABC)
        result = r.removeAttribute("mutable_attr")
        self.assertTrue(result)
        self.assertFalse(hasattr(MutableABC, "mutable_attr"))

    def testRemoveAttributeRaisesValueErrorWhenMissing(self) -> None:
        """
        Assert that removing an absent attribute raises ValueError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        r = ReflectionAbstract(SampleABC)
        with self.assertRaises(ValueError):
            r.removeAttribute("no_such_attribute_xyz")

# ---------------------------------------------------------------------------
# Method inspection
# ---------------------------------------------------------------------------

class TestReflectionAbstractPublicMethods(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for public method tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetPublicMethodsReturnsList(self) -> None:
        """
        Assert that getPublicMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPublicMethods(), list)

    def testConcreteMethodInPublicMethods(self) -> None:
        """
        Assert that 'concrete_method' is included in public methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("concrete_method", self.r.getPublicMethods())

    def testAbstractMethodInPublicMethods(self) -> None:
        """
        Assert that 'abstract_method' is listed in public methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("abstract_method", self.r.getPublicMethods())

    def testProtectedMethodNotInPublicMethods(self) -> None:
        """
        Assert that '_protected_method' is absent from public methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("_protected_method", self.r.getPublicMethods())

    def testGetPublicSyncMethodsReturnsList(self) -> None:
        """
        Assert that getPublicSyncMethods returns a list containing 'concrete_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sync = self.r.getPublicSyncMethods()
        self.assertIsInstance(sync, list)
        self.assertIn("concrete_method", sync)

    def testGetPublicAsyncMethodsReturnsList(self) -> None:
        """
        Assert that getPublicAsyncMethods returns a list containing 'async_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        async_methods = self.r.getPublicAsyncMethods()
        self.assertIsInstance(async_methods, list)
        self.assertIn("async_method", async_methods)

    def testAsyncMethodNotInSyncMethods(self) -> None:
        """
        Assert that 'async_method' is absent from the synchronous method list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("async_method", self.r.getPublicSyncMethods())

    def testGetMethodsReturnsList(self) -> None:
        """
        Assert that getMethods returns a combined list of all non-dunder methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getMethods(), list)


class TestReflectionAbstractProtectedMethods(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for protected method tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetProtectedMethodsReturnsList(self) -> None:
        """
        Assert that getProtectedMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getProtectedMethods(), list)

    def testProtectedMethodPresent(self) -> None:
        """
        Assert that '_protected_method' is listed in protected methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_method", self.r.getProtectedMethods())

    def testPublicMethodNotInProtectedMethods(self) -> None:
        """
        Assert that 'concrete_method' is absent from the protected methods list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("concrete_method", self.r.getProtectedMethods())

    def testGetProtectedSyncMethodsReturnsList(self) -> None:
        """
        Assert that getProtectedSyncMethods contains '_protected_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sync = self.r.getProtectedSyncMethods()
        self.assertIsInstance(sync, list)
        self.assertIn("_protected_method", sync)

    def testGetProtectedAsyncMethodsReturnsList(self) -> None:
        """
        Assert that getProtectedAsyncMethods contains '_protected_async_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        async_methods = self.r.getProtectedAsyncMethods()
        self.assertIsInstance(async_methods, list)
        self.assertIn("_protected_async_method", async_methods)


class TestReflectionAbstractPrivateMethods(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for private method tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetPrivateMethodsReturnsList(self) -> None:
        """
        Assert that getPrivateMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPrivateMethods(), list)

    def testPrivateMethodPresentWithStrippedName(self) -> None:
        """
        Assert that '__private_method' is found with the class prefix removed.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        Python mangles __private_method to _SampleABC__private_method.
        ReflectionAbstract strips '_SampleABC' leaving '__private_method'.
        """
        self.assertIn("__private_method", self.r.getPrivateMethods())

class TestReflectionAbstractClassMethods(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for class method tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetPublicClassMethodsReturnsList(self) -> None:
        """
        Assert that getPublicClassMethods returns a list containing 'class_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getPublicClassMethods()
        self.assertIsInstance(result, list)
        self.assertIn("class_method", result)

    def testProtectedClassMethodPresent(self) -> None:
        """
        Assert that '_protected_class_method' is in protected class methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "_protected_class_method",
            self.r.getProtectedClassMethods(),
        )

    def testGetPrivateClassMethodsReturnsList(self) -> None:
        """
        Assert that getPrivateClassMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPrivateClassMethods(), list)

    def testGetPublicClassSyncMethodsReturnsList(self) -> None:
        """
        Assert that getPublicClassSyncMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPublicClassSyncMethods(), list)

    def testGetProtectedClassSyncMethodsReturnsList(self) -> None:
        """
        Assert that getProtectedClassSyncMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getProtectedClassSyncMethods(), list)

class TestReflectionAbstractStaticMethods(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for static method tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetPublicStaticMethodsReturnsList(self) -> None:
        """
        Assert that getPublicStaticMethods returns a list containing 'static_method'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getPublicStaticMethods()
        self.assertIsInstance(result, list)
        self.assertIn("static_method", result)

    def testProtectedStaticMethodPresent(self) -> None:
        """
        Assert that '_protected_static_method' is in protected static methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "_protected_static_method",
            self.r.getProtectedStaticMethods(),
        )

    def testGetPrivateStaticMethodsReturnsList(self) -> None:
        """
        Assert that getPrivateStaticMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPrivateStaticMethods(), list)

    def testGetPublicStaticSyncMethodsReturnsList(self) -> None:
        """
        Assert that getPublicStaticSyncMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getPublicStaticSyncMethods(), list)

    def testGetProtectedStaticSyncMethodsReturnsList(self) -> None:
        """
        Assert that getProtectedStaticSyncMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getProtectedStaticSyncMethods(), list)

class TestReflectionAbstractDunderMethods(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for dunder method tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetDunderMethodsReturnsList(self) -> None:
        """
        Assert that getDunderMethods returns a list of dunder-named callables.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getDunderMethods(), list)

    def testGetMagicMethodsDelegatesToDunder(self) -> None:
        """
        Assert that getMagicMethods returns the same result as getDunderMethods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.r.getMagicMethods(), self.r.getDunderMethods())

# ---------------------------------------------------------------------------
# Method operations: hasMethod, removeMethod, getMethodSignature
# ---------------------------------------------------------------------------

class TestReflectionAbstractMethodOperations(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for method operation tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testHasMethodReturnsTrueForExisting(self) -> None:
        """
        Assert that hasMethod returns True when the method exists.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(self.r.hasMethod("concrete_method"))

    def testHasMethodReturnsFalseForMissing(self) -> None:
        """
        Assert that hasMethod returns False for an absent method name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertFalse(self.r.hasMethod("totally_fake_method"))

    def testRemoveMethodReturnsTrueOnSuccess(self) -> None:
        """
        Assert that removeMethod returns True and removes the method.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        Verifies removal via hasattr on the class directly, since the
        reflection cache is verified separately in clearCache tests.
        """
        MutableABC = _make_mutable_abc()
        r = ReflectionAbstract(MutableABC)
        result = r.removeMethod("deletable_method")
        self.assertTrue(result)
        self.assertFalse(hasattr(MutableABC, "deletable_method"))

    def testRemoveMethodRaisesValueErrorWhenMissing(self) -> None:
        """
        Assert that removeMethod raises ValueError for a non-existent method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        r = ReflectionAbstract(SampleABC)
        with self.assertRaises(ValueError):
            r.removeMethod("no_such_method_xyz")

    def testGetMethodSignatureReturnsInspectSignature(self) -> None:
        """
        Assert that getMethodSignature returns an inspect.Signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.r.getMethodSignature("concrete_method")
        self.assertIsInstance(sig, inspect.Signature)

    def testGetMethodSignatureRaisesValueErrorForMissing(self) -> None:
        """
        Assert that getMethodSignature raises ValueError for an absent method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ValueError):
            self.r.getMethodSignature("ghost_method")

# ---------------------------------------------------------------------------
# Property inspection
# ---------------------------------------------------------------------------

class TestReflectionAbstractProperties(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for property tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testGetPropertiesReturnsList(self) -> None:
        """
        Assert that getProperties returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.r.getProperties(), list)

    def testPublicPropertyPresent(self) -> None:
        """
        Assert that 'a_property' is found in the list returned by getProperties.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("a_property", self.r.getProperties())

    def testGetPublicPropertiesReturnsList(self) -> None:
        """
        Assert that getPublicProperties returns a list that includes 'a_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getPublicProperties()
        self.assertIsInstance(result, list)
        self.assertIn("a_property", result)

    def testGetProtectedPropertiesReturnsList(self) -> None:
        """
        Assert that getProtectedProperties contains '_protected_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.getProtectedProperties()
        self.assertIsInstance(result, list)
        self.assertIn("_protected_property", result)

    def testGetPrivatePropertiesReturnsList(self) -> None:
        """
        Assert that getPrivateProperties returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        SampleABC has no name-mangled properties, so the list is empty.
        """
        self.assertIsInstance(self.r.getPrivateProperties(), list)

    def testGetPropertySignatureReturnsInspectSignature(self) -> None:
        """
        Assert that getPropertySignature returns an inspect.Signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.r.getPropertySignature("a_property")
        self.assertIsInstance(sig, inspect.Signature)

    def testGetPropertySignatureRaisesForMissingProperty(self) -> None:
        """
        Assert that getPropertySignature raises when the property is absent.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises((ValueError, TypeError)):
            self.r.getPropertySignature("nonexistent_prop")

    def testGetPropertyDocstringReturnsStr(self) -> None:
        """
        Assert that getPropertyDocstring returns a str for 'a_property'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        doc = self.r.getPropertyDocstring("a_property")
        self.assertIsInstance(doc, str)

    def testGetPropertyDocstringRaisesForMissing(self) -> None:
        """
        Assert that getPropertyDocstring raises for an unknown property name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises((ValueError, TypeError)):
            self.r.getPropertyDocstring("nonexistent_prop")

# ---------------------------------------------------------------------------
# Dependency signatures and cache
# ---------------------------------------------------------------------------

class TestReflectionAbstractDependencies(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for dependency tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testConstructorSignatureReturnsSignatureObject(self) -> None:
        """
        Assert that constructorSignature returns a non-None Signature object.

        Returns
        -------
        None
            Raises AssertionError on failure.

        Notes
        -----
        The exact type is from
        orionis.services.introspection.dependencies.entities.
        """
        sig = self.r.constructorSignature()
        self.assertIsNotNone(sig)

    def testMethodSignatureReturnsSignatureObject(self) -> None:
        """
        Assert that methodSignature returns a non-None Signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = self.r.methodSignature("concrete_method")
        self.assertIsNotNone(sig)

    def testMethodSignatureRaisesAttributeErrorForMissing(self) -> None:
        """
        Assert that methodSignature raises AttributeError for an absent method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(AttributeError):
            self.r.methodSignature("ghost_method_xyz")

class TestReflectionAbstractClearCache(TestCase):

    def setUp(self) -> None:
        """Initialise a shared ReflectionAbstract for clearCache tests."""
        self.r = ReflectionAbstract(SampleABC)

    def testClearCacheResetsStoredValues(self) -> None:
        """
        Assert that clearCache removes manually stored cache entries.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.r["some_cached_key"] = "value"
        self.r.clearCache()
        self.assertNotIn("some_cached_key", self.r)

    def testClearCacheAllowsRecomputation(self) -> None:
        """
        Assert that methods still return correct results after clearCache.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # Populate the cache, then clear it to force fresh computation
        _ = self.r.getPublicMethods()
        self.r.clearCache()
        methods = self.r.getPublicMethods()
        self.assertIn("concrete_method", methods)

    def testClearCacheReturnsNone(self) -> None:
        """
        Assert that clearCache has no return value.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.r.clearCache()
        self.assertIsNone(result)
