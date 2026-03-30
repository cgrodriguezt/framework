import inspect
from abc import ABC
from orionis.test import TestCase
from orionis.services.introspection.callables.contracts.reflection import (
    IReflectionCallable,
)

# ---------------------------------------------------------------------------
# Minimal concrete implementation used only in contract tests
# ---------------------------------------------------------------------------

class _StubCallable(IReflectionCallable):
    """Minimal concrete stub that satisfies all abstract methods."""

    def getCallable(self) -> callable:
        return lambda: None

    def getName(self) -> str:
        return "stub"

    def getModuleName(self) -> str:
        return "stub_module"

    def getModuleWithCallableName(self) -> str:
        return "stub_module.stub"

    def getDocstring(self) -> str:
        return "stub docstring"

    def getSourceCode(self) -> str:
        return "def stub(): pass"

    def getFile(self) -> str:
        return "/stub/file.py"

    def getSignature(self) -> inspect.Signature:
        return inspect.signature(lambda: None)

    def getDependencies(self):
        return None

    def clearCache(self) -> None:
        pass

# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------

class TestIReflectionCallableIsABC(TestCase):

    def testIsAbstractBaseClass(self) -> None:
        """
        Assert that IReflectionCallable inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IReflectionCallable, ABC))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating IReflectionCallable directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IReflectionCallable()  # type: ignore[abstract]

    def testConcreteSubclassInstantiates(self) -> None:
        """
        Assert that a concrete subclass implementing all methods can be created.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        stub = _StubCallable()
        self.assertIsInstance(stub, IReflectionCallable)

class TestIReflectionCallableAbstractMethods(TestCase):

    def testGetCallableIsAbstract(self) -> None:
        """
        Assert that getCallable is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getCallable", IReflectionCallable.__abstractmethods__)

    def testGetNameIsAbstract(self) -> None:
        """
        Assert that getName is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getName", IReflectionCallable.__abstractmethods__)

    def testGetModuleNameIsAbstract(self) -> None:
        """
        Assert that getModuleName is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getModuleName", IReflectionCallable.__abstractmethods__)

    def testGetModuleWithCallableNameIsAbstract(self) -> None:
        """
        Assert that getModuleWithCallableName is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn(
            "getModuleWithCallableName",
            IReflectionCallable.__abstractmethods__,
        )

    def testGetDocstringIsAbstract(self) -> None:
        """
        Assert that getDocstring is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getDocstring", IReflectionCallable.__abstractmethods__)

    def testGetSourceCodeIsAbstract(self) -> None:
        """
        Assert that getSourceCode is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getSourceCode", IReflectionCallable.__abstractmethods__)

    def testGetFileIsAbstract(self) -> None:
        """
        Assert that getFile is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getFile", IReflectionCallable.__abstractmethods__)

    def testGetSignatureIsAbstract(self) -> None:
        """
        Assert that getSignature is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getSignature", IReflectionCallable.__abstractmethods__)

    def testGetDependenciesIsAbstract(self) -> None:
        """
        Assert that getDependencies is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("getDependencies", IReflectionCallable.__abstractmethods__)

    def testClearCacheIsAbstract(self) -> None:
        """
        Assert that clearCache is registered as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("clearCache", IReflectionCallable.__abstractmethods__)

class TestIReflectionCallablePartialImplementation(TestCase):

    def testMissingOneMethodRaisesTypeError(self) -> None:
        """
        Assert that a subclass missing clearCache cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        class _Partial(IReflectionCallable):
            def getCallable(self): return None
            def getName(self): return ""
            def getModuleName(self): return ""
            def getModuleWithCallableName(self): return ""
            def getDocstring(self): return ""
            def getSourceCode(self): return ""
            def getFile(self): return ""
            def getSignature(self): return None
            def getDependencies(self): return None
            # clearCache intentionally omitted

        with self.assertRaises(TypeError):
            _Partial()

class TestIReflectionCallableStubContract(TestCase):

    def setUp(self) -> None:
        """Initialise a shared stub instance for contract return-type tests."""
        self.stub = _StubCallable()

    def testGetCallableReturnsCallable(self) -> None:
        """
        Assert that getCallable returns a callable object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(callable(self.stub.getCallable()))

    def testGetNameReturnsStr(self) -> None:
        """
        Assert that getName returns a str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getName(), str)

    def testGetModuleNameReturnsStr(self) -> None:
        """
        Assert that getModuleName returns a str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getModuleName(), str)

    def testGetModuleWithCallableNameReturnsStr(self) -> None:
        """
        Assert that getModuleWithCallableName returns a str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getModuleWithCallableName(), str)

    def testGetDocstringReturnsStr(self) -> None:
        """
        Assert that getDocstring returns a str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getDocstring(), str)

    def testGetSourceCodeReturnsStr(self) -> None:
        """
        Assert that getSourceCode returns a str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getSourceCode(), str)

    def testGetFileReturnsStr(self) -> None:
        """
        Assert that getFile returns a str.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getFile(), str)

    def testGetSignatureReturnsInspectSignature(self) -> None:
        """
        Assert that getSignature returns an inspect.Signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getSignature(), inspect.Signature)

    def testClearCacheReturnsNone(self) -> None:
        """
        Assert that clearCache returns None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.stub.clearCache())
