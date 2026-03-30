import os as _os_mod
import sys
import types
from orionis.test import TestCase
from orionis.services.introspection.modules.reflection import ReflectionModule

# ---------------------------------------------------------------------------
# Synthetic fixture module
# ---------------------------------------------------------------------------
# A fully controlled module is injected into sys.modules so that tests can
# assert exact keys without depending on a real file on disk.

_FIXTURE_NAME = "_orionis_module_test_fixture"


def _build_fixture() -> types.ModuleType:
    """
    Build and register a synthetic test module in sys.modules.

    Returns
    -------
    types.ModuleType
        The synthetic module registered under _FIXTURE_NAME.
    """
    mod = types.ModuleType(_FIXTURE_NAME)

    # --- classes ---
    class PublicClass:
        """Public class fixture."""

    class _ProtectedClass:
        """Protected class fixture."""

    # --- functions ---
    def public_sync_fn() -> int:
        """Public synchronous function."""
        return 1

    async def public_async_fn() -> int:
        """Public asynchronous function."""
        return 2

    def _protected_sync_fn() -> int:
        """Protected synchronous function."""
        return 3

    async def _protected_async_fn() -> int:
        """Protected asynchronous function."""
        return 4

    # Public constant (uppercase name, non-callable)
    mod.PUBLIC_CONST = 42

    # Inject classes
    mod.PublicClass = PublicClass
    mod._ProtectedClass = _ProtectedClass

    # Inject functions
    mod.public_sync_fn = public_sync_fn
    mod.public_async_fn = public_async_fn
    mod._protected_sync_fn = _protected_sync_fn
    mod._protected_async_fn = _protected_async_fn

    # Inject a module-level import so getImports() has something to find
    mod.os = _os_mod

    sys.modules[_FIXTURE_NAME] = mod
    return mod


_FIXTURE_MODULE = _build_fixture()

# Real module used for getFile / getSourceCode tests
_REAL_MODULE = "orionis.services.introspection.modules.reflection"


class TestReflectionModuleInit(TestCase):
    """
    Verify the constructor validation logic of ReflectionModule.

    Methods
    -------
    testInitWithValidModuleSucceeds
    testInitWithNonStringRaisesTypeError
    testInitWithEmptyStringRaisesTypeError
    testInitWithNonExistentModuleRaisesTypeError
    """

    def testInitWithValidModuleSucceeds(self) -> None:
        """
        Assert that a valid importable module name creates an instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        rm = ReflectionModule(_FIXTURE_NAME)
        self.assertIsInstance(rm, ReflectionModule)

    def testInitWithNonStringRaisesTypeError(self) -> None:
        """
        Assert that passing a non-string value raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ReflectionModule(123)

    def testInitWithEmptyStringRaisesTypeError(self) -> None:
        """
        Assert that an empty string raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ReflectionModule("")

    def testInitWithNonExistentModuleRaisesTypeError(self) -> None:
        """
        Assert that an unknown module name raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            ReflectionModule("this.module.does.not.exist.xyz")


class TestReflectionModuleCacheProtocol(TestCase):
    """
    Verify the internal cache protocol (__getitem__, __setitem__,
    __contains__, __delitem__).

    Methods
    -------
    setUp
    testSetAndGetCacheItem
    testContainsReturnsTrueForExistingKey
    testContainsReturnsFalseForMissingKey
    testDeleteCacheItem
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule for cache protocol tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testSetAndGetCacheItem(self) -> None:
        """
        Assert that a value stored with __setitem__ is retrievable via
        __getitem__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm["test_key"] = "test_value"
        self.assertEqual(self.rm["test_key"], "test_value")

    def testContainsReturnsTrueForExistingKey(self) -> None:
        """
        Assert that __contains__ returns True for a key that was stored.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm["present"] = 1
        self.assertIn("present", self.rm)

    def testContainsReturnsFalseForMissingKey(self) -> None:
        """
        Assert that __contains__ returns False for an absent key.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("absent_key_xyz", self.rm)

    def testDeleteCacheItem(self) -> None:
        """
        Assert that __delitem__ removes the key from the cache.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm["to_delete"] = "bye"
        del self.rm["to_delete"]
        self.assertNotIn("to_delete", self.rm)


class TestReflectionModuleGetModule(TestCase):
    """
    Verify that getModule returns the imported module object.

    Methods
    -------
    setUp
    testGetModuleReturnsSameObject
    testGetModuleIsModuleType
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule wrapping the synthetic fixture.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testGetModuleReturnsSameObject(self) -> None:
        """
        Assert that getModule returns the exact registered fixture module.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIs(self.rm.getModule(), sys.modules[_FIXTURE_NAME])

    def testGetModuleIsModuleType(self) -> None:
        """
        Assert that getModule return value is a ModuleType instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getModule(), types.ModuleType)


class TestReflectionModuleClasses(TestCase):
    """
    Verify class discovery and manipulation methods.

    Methods
    -------
    setUp
    testGetClassesReturnsDict
    testGetClassesContainsPublicClass
    testGetPublicClassesContainsPublicClass
    testGetPublicClassesExcludesProtected
    testGetProtectedClassesContainsProtectedClass
    testGetPrivateClassesReturnsEmptyDict
    testHasClassReturnsTrueForExisting
    testHasClassReturnsFalseForMissing
    testGetClassReturnsCorrectType
    testGetClassReturnsNoneForMissing
    testSetClassReturnsTrueAndIsVisible
    testSetClassWithNonTypeRaisesTypeError
    testSetClassWithInvalidNameRaisesValueError
    testSetClassWithKeywordRaisesValueError
    testRemoveClassReturnsTrueAndIsGone
    testRemoveClassNonExistingRaisesValueError
    """

    def setUp(self) -> None:
        """
        Instantiate a fresh ReflectionModule for class-related tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # Re-build fixture to guarantee isolation between mutation tests
        _build_fixture()
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testGetClassesReturnsDict(self) -> None:
        """
        Assert that getClasses returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getClasses(), dict)

    def testGetClassesContainsPublicClass(self) -> None:
        """
        Assert that getClasses includes 'PublicClass'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("PublicClass", self.rm.getClasses())

    def testGetPublicClassesContainsPublicClass(self) -> None:
        """
        Assert that getPublicClasses includes 'PublicClass'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("PublicClass", self.rm.getPublicClasses())

    def testGetPublicClassesExcludesProtected(self) -> None:
        """
        Assert that getPublicClasses excludes '_ProtectedClass'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("_ProtectedClass", self.rm.getPublicClasses())

    def testGetProtectedClassesContainsProtectedClass(self) -> None:
        """
        Assert that getProtectedClasses includes '_ProtectedClass'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_ProtectedClass", self.rm.getProtectedClasses())

    def testGetPrivateClassesReturnsEmptyDict(self) -> None:
        """
        Assert that getPrivateClasses returns an empty dict for the fixture.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.rm.getPrivateClasses(), {})

    def testHasClassReturnsTrueForExisting(self) -> None:
        """
        Assert that hasClass returns True for 'PublicClass'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(self.rm.hasClass("PublicClass"))

    def testHasClassReturnsFalseForMissing(self) -> None:
        """
        Assert that hasClass returns False for an unknown class name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertFalse(self.rm.hasClass("NonExistentXyz"))

    def testGetClassReturnsCorrectType(self) -> None:
        """
        Assert that getClass returns a type object for 'PublicClass'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        cls = self.rm.getClass("PublicClass")
        self.assertIsNotNone(cls)
        self.assertTrue(isinstance(cls, type))

    def testGetClassReturnsNoneForMissing(self) -> None:
        """
        Assert that getClass returns None for an unknown class name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.rm.getClass("NonExistentXyz"))

    def testSetClassReturnsTrueAndIsVisible(self) -> None:
        """
        Assert that setClass injects the class and it is then discoverable.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """

        class InjectedClass:
            """Dynamically injected class."""

        result = self.rm.setClass("InjectedClass", InjectedClass)
        self.assertTrue(result)
        self.assertTrue(self.rm.hasClass("InjectedClass"))
        # cleanup
        self.rm.removeClass("InjectedClass")

    def testSetClassWithNonTypeRaisesTypeError(self) -> None:
        """
        Assert that setClass raises TypeError when the value is not a type.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            self.rm.setClass("Bad", "not_a_class")

    def testSetClassWithInvalidNameRaisesValueError(self) -> None:
        """
        Assert that setClass raises ValueError for an invalid identifier.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ValueError):
            self.rm.setClass("123invalid", int)

    def testSetClassWithKeywordRaisesValueError(self) -> None:
        """
        Assert that setClass raises ValueError when the name is a keyword.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ValueError):
            self.rm.setClass("class", int)

    def testRemoveClassReturnsTrueAndIsGone(self) -> None:
        """
        Assert that removeClass removes the class from the module.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """

        class TempClass:
            """Temporary class for removal test."""

        self.rm.setClass("TempClass", TempClass)
        result = self.rm.removeClass("TempClass")
        self.assertTrue(result)
        self.assertFalse(self.rm.hasClass("TempClass"))

    def testRemoveClassNonExistingRaisesValueError(self) -> None:
        """
        Assert that removeClass raises ValueError for an unknown class name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ValueError):
            self.rm.removeClass("NonExistentXyz")


class TestReflectionModuleConstants(TestCase):
    """
    Verify constant discovery methods.

    Methods
    -------
    setUp
    testGetConstantsReturnsDict
    testGetConstantsContainsPublicConst
    testGetPublicConstantsContainsPublicConst
    testGetProtectedConstantsReturnsDict
    testGetPrivateConstantsReturnsDict
    testGetConstantReturnsCorrectValue
    testGetConstantReturnsNoneForMissing
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule for constant discovery tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testGetConstantsReturnsDict(self) -> None:
        """
        Assert that getConstants returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getConstants(), dict)

    def testGetConstantsContainsPublicConst(self) -> None:
        """
        Assert that getConstants includes 'PUBLIC_CONST'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("PUBLIC_CONST", self.rm.getConstants())

    def testGetPublicConstantsContainsPublicConst(self) -> None:
        """
        Assert that getPublicConstants includes 'PUBLIC_CONST'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("PUBLIC_CONST", self.rm.getPublicConstants())

    def testGetProtectedConstantsReturnsDict(self) -> None:
        """
        Assert that getProtectedConstants returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getProtectedConstants(), dict)

    def testGetPrivateConstantsReturnsDict(self) -> None:
        """
        Assert that getPrivateConstants returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getPrivateConstants(), dict)

    def testGetConstantReturnsCorrectValue(self) -> None:
        """
        Assert that getConstant returns 42 for 'PUBLIC_CONST'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(self.rm.getConstant("PUBLIC_CONST"), 42)

    def testGetConstantReturnsNoneForMissing(self) -> None:
        """
        Assert that getConstant returns None for an unknown constant name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.rm.getConstant("NONEXISTENT_XYZ"))


class TestReflectionModulePublicFunctions(TestCase):
    """
    Verify public function discovery (all, sync, async).

    Methods
    -------
    setUp
    testGetFunctionsReturnsDict
    testGetFunctionsContainsPublicSyncFn
    testGetPublicFunctionsContainsPublicSyncFn
    testGetPublicFunctionsExcludesProtected
    testGetPublicSyncFunctionsContainsSyncFn
    testGetPublicSyncFunctionsExcludesAsyncFn
    testGetPublicAsyncFunctionsContainsAsyncFn
    testGetPublicAsyncFunctionsExcludesSyncFn
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule for public function tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testGetFunctionsReturnsDict(self) -> None:
        """
        Assert that getFunctions returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getFunctions(), dict)

    def testGetFunctionsContainsPublicSyncFn(self) -> None:
        """
        Assert that getFunctions includes 'public_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_sync_fn", self.rm.getFunctions())

    def testGetPublicFunctionsContainsPublicSyncFn(self) -> None:
        """
        Assert that getPublicFunctions includes 'public_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_sync_fn", self.rm.getPublicFunctions())

    def testGetPublicFunctionsExcludesProtected(self) -> None:
        """
        Assert that getPublicFunctions excludes '_protected_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("_protected_sync_fn", self.rm.getPublicFunctions())

    def testGetPublicSyncFunctionsContainsSyncFn(self) -> None:
        """
        Assert that getPublicSyncFunctions includes 'public_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_sync_fn", self.rm.getPublicSyncFunctions())

    def testGetPublicSyncFunctionsExcludesAsyncFn(self) -> None:
        """
        Assert that getPublicSyncFunctions excludes 'public_async_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("public_async_fn", self.rm.getPublicSyncFunctions())

    def testGetPublicAsyncFunctionsContainsAsyncFn(self) -> None:
        """
        Assert that getPublicAsyncFunctions includes 'public_async_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("public_async_fn", self.rm.getPublicAsyncFunctions())

    def testGetPublicAsyncFunctionsExcludesSyncFn(self) -> None:
        """
        Assert that getPublicAsyncFunctions excludes 'public_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("public_sync_fn", self.rm.getPublicAsyncFunctions())


class TestReflectionModuleProtectedFunctions(TestCase):
    """
    Verify protected function discovery (all, sync, async).

    Methods
    -------
    setUp
    testGetProtectedFunctionsContainsProtectedSyncFn
    testGetProtectedFunctionsExcludesPublic
    testGetProtectedSyncFunctionsContainsSyncFn
    testGetProtectedSyncFunctionsExcludesAsyncFn
    testGetProtectedAsyncFunctionsContainsAsyncFn
    testGetProtectedAsyncFunctionsExcludesSyncFn
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule for protected function tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testGetProtectedFunctionsContainsProtectedSyncFn(self) -> None:
        """
        Assert that getProtectedFunctions includes '_protected_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_sync_fn", self.rm.getProtectedFunctions())

    def testGetProtectedFunctionsExcludesPublic(self) -> None:
        """
        Assert that getProtectedFunctions excludes 'public_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn("public_sync_fn", self.rm.getProtectedFunctions())

    def testGetProtectedSyncFunctionsContainsSyncFn(self) -> None:
        """
        Assert that getProtectedSyncFunctions includes '_protected_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_sync_fn", self.rm.getProtectedSyncFunctions())

    def testGetProtectedSyncFunctionsExcludesAsyncFn(self) -> None:
        """
        Assert that getProtectedSyncFunctions excludes '_protected_async_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn(
            "_protected_async_fn",
            self.rm.getProtectedSyncFunctions(),
        )

    def testGetProtectedAsyncFunctionsContainsAsyncFn(self) -> None:
        """
        Assert that getProtectedAsyncFunctions includes '_protected_async_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("_protected_async_fn", self.rm.getProtectedAsyncFunctions())

    def testGetProtectedAsyncFunctionsExcludesSyncFn(self) -> None:
        """
        Assert that getProtectedAsyncFunctions excludes '_protected_sync_fn'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertNotIn(
            "_protected_sync_fn",
            self.rm.getProtectedAsyncFunctions(),
        )


class TestReflectionModulePrivateFunctions(TestCase):
    """
    Verify private function discovery returns empty dicts for the fixture.

    Methods
    -------
    setUp
    testGetPrivateFunctionsReturnsDict
    testGetPrivateSyncFunctionsReturnsDict
    testGetPrivateAsyncFunctionsReturnsDict
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule for private function tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testGetPrivateFunctionsReturnsDict(self) -> None:
        """
        Assert that getPrivateFunctions returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getPrivateFunctions(), dict)

    def testGetPrivateSyncFunctionsReturnsDict(self) -> None:
        """
        Assert that getPrivateSyncFunctions returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getPrivateSyncFunctions(), dict)

    def testGetPrivateAsyncFunctionsReturnsDict(self) -> None:
        """
        Assert that getPrivateAsyncFunctions returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getPrivateAsyncFunctions(), dict)


class TestReflectionModuleImports(TestCase):
    """
    Verify that getImports detects module-level imports.

    Methods
    -------
    setUp
    testGetImportsReturnsDict
    testGetImportsContainsOsModule
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule for import discovery tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testGetImportsReturnsDict(self) -> None:
        """
        Assert that getImports returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.rm.getImports(), dict)

    def testGetImportsContainsOsModule(self) -> None:
        """
        Assert that getImports includes the 'os' attribute injected into the
        fixture module.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("os", self.rm.getImports())


class TestReflectionModuleFileAndSource(TestCase):
    """
    Verify getFile and getSourceCode against a real file-backed module.

    Methods
    -------
    setUp
    testGetFileReturnsNonEmptyString
    testGetFileEndsWithPyExtension
    testGetSourceCodeReturnsNonEmptyString
    testGetSourceCodeContainsClassName
    testGetSourceCodeIsCached
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule wrapping the real reflection module.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_REAL_MODULE)

    def testGetFileReturnsNonEmptyString(self) -> None:
        """
        Assert that getFile returns a non-empty string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        path = self.rm.getFile()
        self.assertIsInstance(path, str)
        self.assertGreater(len(path), 0)

    def testGetFileEndsWithPyExtension(self) -> None:
        """
        Assert that getFile returns a path ending with '.py' or '.pyc'.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        path = self.rm.getFile()
        self.assertTrue(path.endswith(".py") or path.endswith(".pyc"))

    def testGetSourceCodeReturnsNonEmptyString(self) -> None:
        """
        Assert that getSourceCode returns a non-empty string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        src = self.rm.getSourceCode()
        self.assertIsInstance(src, str)
        self.assertGreater(len(src), 0)

    def testGetSourceCodeContainsClassName(self) -> None:
        """
        Assert that the source code contains the 'ReflectionModule' class name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("ReflectionModule", self.rm.getSourceCode())

    def testGetSourceCodeIsCached(self) -> None:
        """
        Assert that repeated calls to getSourceCode return the same object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        first = self.rm.getSourceCode()
        second = self.rm.getSourceCode()
        self.assertIs(first, second)


class TestReflectionModuleClearCache(TestCase):
    """
    Verify that clearCache empties the internal cache.

    Methods
    -------
    setUp
    testClearCacheReturnsNone
    testClearCacheInvalidatesStoredItems
    testClearCacheForcesFreshComputation
    """

    def setUp(self) -> None:
        """
        Instantiate a ReflectionModule for cache clearing tests.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm = ReflectionModule(_FIXTURE_NAME)

    def testClearCacheReturnsNone(self) -> None:
        """
        Assert that clearCache returns None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.rm.clearCache())

    def testClearCacheInvalidatesStoredItems(self) -> None:
        """
        Assert that after clearCache, previously cached items are absent.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.rm["sentinel"] = "value"
        self.rm.clearCache()
        self.assertNotIn("sentinel", self.rm)

    def testClearCacheForcesFreshComputation(self) -> None:
        """
        Assert that getClasses recomputes correctly after clearCache is called.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        # Populate the classes cache
        _ = self.rm.getClasses()
        self.assertIn("classes", self.rm)
        # Clear and verify the cache key is gone
        self.rm.clearCache()
        self.assertNotIn("classes", self.rm)
        # Recompute and check result is still valid
        self.assertIsInstance(self.rm.getClasses(), dict)
