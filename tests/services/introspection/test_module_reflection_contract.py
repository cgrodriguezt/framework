from abc import ABC
from orionis.test import TestCase
from orionis.services.introspection.modules.contracts.reflection import (
    IReflectionModule,
)


class _StubModule(IReflectionModule):
    """
    Minimal concrete implementation of IReflectionModule for contract tests.

    Implements every abstract method with the simplest possible body so
    that the stub can be instantiated and return types can be verified.
    """

    def getModule(self):
        return object()

    def hasClass(self, class_name):
        return False

    def getClass(self, class_name):
        return None

    def setClass(self, class_name, cls):
        return True

    def removeClass(self, class_name):
        return True

    def getClasses(self):
        return {}

    def getPublicClasses(self):
        return {}

    def getProtectedClasses(self):
        return {}

    def getPrivateClasses(self):
        return {}

    def getConstant(self, constant_name):
        return None

    def getConstants(self):
        return {}

    def getPublicConstants(self):
        return {}

    def getProtectedConstants(self):
        return {}

    def getPrivateConstants(self):
        return {}

    def getFunctions(self):
        return {}

    def getPublicFunctions(self):
        return {}

    def getPublicSyncFunctions(self):
        return {}

    def getPublicAsyncFunctions(self):
        return {}

    def getProtectedFunctions(self):
        return {}

    def getProtectedSyncFunctions(self):
        return {}

    def getProtectedAsyncFunctions(self):
        return {}

    def getPrivateFunctions(self):
        return {}

    def getPrivateSyncFunctions(self):
        return {}

    def getPrivateAsyncFunctions(self):
        return {}

    def getImports(self):
        return {}

    def getFile(self):
        return ""

    def getSourceCode(self):
        return ""

    def clearCache(self):
        return None


class _OnlyGetModule(IReflectionModule):
    """
    Partial stub that implements only getModule.

    Used to verify that a class missing the remaining abstract methods
    cannot be instantiated, raising TypeError.
    """

    def getModule(self):
        return object()


class TestIReflectionModuleIsABC(TestCase):
    """
    Verify the ABC characteristics of IReflectionModule.

    Methods
    -------
    testIsABC
    testDirectInstantiationRaisesTypeError
    testStubCanBeInstantiated
    """

    def testIsABC(self) -> None:
        """
        Assert that IReflectionModule inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IReflectionModule, ABC))

    def testDirectInstantiationRaisesTypeError(self) -> None:
        """
        Assert that direct instantiation of IReflectionModule raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IReflectionModule()

    def testStubCanBeInstantiated(self) -> None:
        """
        Assert that a complete stub implementation can be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        stub = _StubModule()
        self.assertIsInstance(stub, IReflectionModule)


class TestIReflectionModuleAbstractMethods(TestCase):
    """
    Verify that every declared method of IReflectionModule is abstract.

    Methods
    -------
    testGetModuleIsAbstract
    testHasClassIsAbstract
    testGetClassIsAbstract
    testSetClassIsAbstract
    testRemoveClassIsAbstract
    testGetClassesIsAbstract
    testGetPublicClassesIsAbstract
    testGetProtectedClassesIsAbstract
    testGetPrivateClassesIsAbstract
    testGetConstantIsAbstract
    testGetConstantsIsAbstract
    testGetPublicConstantsIsAbstract
    testGetProtectedConstantsIsAbstract
    testGetPrivateConstantsIsAbstract
    testGetFunctionsIsAbstract
    testGetPublicFunctionsIsAbstract
    testGetPublicSyncFunctionsIsAbstract
    testGetPublicAsyncFunctionsIsAbstract
    testGetProtectedFunctionsIsAbstract
    testGetProtectedSyncFunctionsIsAbstract
    testGetProtectedAsyncFunctionsIsAbstract
    testGetPrivateFunctionsIsAbstract
    testGetPrivateSyncFunctionsIsAbstract
    testGetPrivateAsyncFunctionsIsAbstract
    testGetImportsIsAbstract
    testGetFileIsAbstract
    testGetSourceCodeIsAbstract
    testClearCacheIsAbstract
    """

    def _assertAbstract(self, name: str) -> None:
        self.assertIn(name, IReflectionModule.__abstractmethods__)

    def testGetModuleIsAbstract(self) -> None:
        """
        Assert that getModule is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getModule")

    def testHasClassIsAbstract(self) -> None:
        """
        Assert that hasClass is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("hasClass")

    def testGetClassIsAbstract(self) -> None:
        """
        Assert that getClass is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getClass")

    def testSetClassIsAbstract(self) -> None:
        """
        Assert that setClass is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("setClass")

    def testRemoveClassIsAbstract(self) -> None:
        """
        Assert that removeClass is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("removeClass")

    def testGetClassesIsAbstract(self) -> None:
        """
        Assert that getClasses is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getClasses")

    def testGetPublicClassesIsAbstract(self) -> None:
        """
        Assert that getPublicClasses is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicClasses")

    def testGetProtectedClassesIsAbstract(self) -> None:
        """
        Assert that getProtectedClasses is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedClasses")

    def testGetPrivateClassesIsAbstract(self) -> None:
        """
        Assert that getPrivateClasses is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateClasses")

    def testGetConstantIsAbstract(self) -> None:
        """
        Assert that getConstant is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getConstant")

    def testGetConstantsIsAbstract(self) -> None:
        """
        Assert that getConstants is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getConstants")

    def testGetPublicConstantsIsAbstract(self) -> None:
        """
        Assert that getPublicConstants is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicConstants")

    def testGetProtectedConstantsIsAbstract(self) -> None:
        """
        Assert that getProtectedConstants is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedConstants")

    def testGetPrivateConstantsIsAbstract(self) -> None:
        """
        Assert that getPrivateConstants is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateConstants")

    def testGetFunctionsIsAbstract(self) -> None:
        """
        Assert that getFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getFunctions")

    def testGetPublicFunctionsIsAbstract(self) -> None:
        """
        Assert that getPublicFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicFunctions")

    def testGetPublicSyncFunctionsIsAbstract(self) -> None:
        """
        Assert that getPublicSyncFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicSyncFunctions")

    def testGetPublicAsyncFunctionsIsAbstract(self) -> None:
        """
        Assert that getPublicAsyncFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicAsyncFunctions")

    def testGetProtectedFunctionsIsAbstract(self) -> None:
        """
        Assert that getProtectedFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedFunctions")

    def testGetProtectedSyncFunctionsIsAbstract(self) -> None:
        """
        Assert that getProtectedSyncFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedSyncFunctions")

    def testGetProtectedAsyncFunctionsIsAbstract(self) -> None:
        """
        Assert that getProtectedAsyncFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedAsyncFunctions")

    def testGetPrivateFunctionsIsAbstract(self) -> None:
        """
        Assert that getPrivateFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateFunctions")

    def testGetPrivateSyncFunctionsIsAbstract(self) -> None:
        """
        Assert that getPrivateSyncFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateSyncFunctions")

    def testGetPrivateAsyncFunctionsIsAbstract(self) -> None:
        """
        Assert that getPrivateAsyncFunctions is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateAsyncFunctions")

    def testGetImportsIsAbstract(self) -> None:
        """
        Assert that getImports is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getImports")

    def testGetFileIsAbstract(self) -> None:
        """
        Assert that getFile is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getFile")

    def testGetSourceCodeIsAbstract(self) -> None:
        """
        Assert that getSourceCode is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getSourceCode")

    def testClearCacheIsAbstract(self) -> None:
        """
        Assert that clearCache is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("clearCache")


class TestIReflectionModulePartialImplementation(TestCase):
    """
    Verify that a partial implementation of IReflectionModule raises TypeError.

    Methods
    -------
    testPartialImplementationRaisesTypeError
    """

    def testPartialImplementationRaisesTypeError(self) -> None:
        """
        Assert that instantiating a class with only one method implemented
        raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _OnlyGetModule()


class TestIReflectionModuleStubReturnTypes(TestCase):
    """
    Verify the return types produced by the _StubModule implementation.

    Methods
    -------
    setUp
    testGetModuleReturnsObject
    testHasClassReturnsBool
    testGetClassReturnsNone
    testGetClassesReturnsDict
    testGetPublicClassesReturnsDict
    testGetConstantsReturnsDict
    testGetFunctionsReturnsDict
    testGetImportsReturnsDict
    testGetFileReturnsStr
    testGetSourceCodeReturnsStr
    testClearCacheReturnsNone
    """

    def setUp(self) -> None:
        """
        Instantiate the stub before each test.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.stub = _StubModule()

    def testGetModuleReturnsObject(self) -> None:
        """
        Assert that getModule returns an object instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getModule(), object)

    def testHasClassReturnsBool(self) -> None:
        """
        Assert that hasClass returns a boolean value.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.hasClass("Any"), bool)

    def testGetClassReturnsNone(self) -> None:
        """
        Assert that getClass returns None when the class is not present.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.stub.getClass("Missing"))

    def testGetClassesReturnsDict(self) -> None:
        """
        Assert that getClasses returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getClasses(), dict)

    def testGetPublicClassesReturnsDict(self) -> None:
        """
        Assert that getPublicClasses returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getPublicClasses(), dict)

    def testGetConstantsReturnsDict(self) -> None:
        """
        Assert that getConstants returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getConstants(), dict)

    def testGetFunctionsReturnsDict(self) -> None:
        """
        Assert that getFunctions returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getFunctions(), dict)

    def testGetImportsReturnsDict(self) -> None:
        """
        Assert that getImports returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getImports(), dict)

    def testGetFileReturnsStr(self) -> None:
        """
        Assert that getFile returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getFile(), str)

    def testGetSourceCodeReturnsStr(self) -> None:
        """
        Assert that getSourceCode returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getSourceCode(), str)

    def testClearCacheReturnsNone(self) -> None:
        """
        Assert that clearCache returns None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.stub.clearCache())
