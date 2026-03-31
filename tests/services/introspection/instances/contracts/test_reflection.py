import inspect
from abc import ABC
from orionis.test import TestCase
from orionis.services.introspection.instances.contracts.reflection import (
    IReflectionInstance,
)

class _StubInstance(IReflectionInstance):
    """
    Minimal concrete implementation of IReflectionInstance for contract tests.

    Implements every abstract method with the simplest possible body so that
    the stub can be instantiated and its return types can be verified.
    """

    def getInstance(self):
        return object()

    def getClass(self):
        return object

    def getClassName(self):
        return "object"

    def getModuleName(self):
        return "builtins"

    def getModuleWithClassName(self):
        return "builtins.object"

    def getDocstring(self):
        return None

    def getBaseClasses(self):
        return (object,)

    def getSourceCode(self, method=None):
        return None

    def getFile(self):
        return None

    def getAnnotations(self):
        return {}

    def hasAttribute(self, name):
        return False

    def getAttribute(self, name, default=None):
        return default

    def setAttribute(self, name, value):
        return True

    def removeAttribute(self, name):
        return True

    def getAttributes(self):
        return {}

    def getPublicAttributes(self):
        return {}

    def getProtectedAttributes(self):
        return {}

    def getPrivateAttributes(self):
        return {}

    def getDunderAttributes(self):
        return {}

    def getMagicAttributes(self):
        return {}

    def hasMethod(self, name):
        return False

    def setMethod(self, name, method):
        return True

    def removeMethod(self, name):
        return None

    def getMethodSignature(self, name):
        return inspect.signature(lambda: None)

    def getMethodDocstring(self, name):
        return None

    def getMethods(self):
        return []

    def getPublicMethods(self):
        return []

    def getPublicSyncMethods(self):
        return []

    def getPublicAsyncMethods(self):
        return []

    def getProtectedMethods(self):
        return []

    def getProtectedSyncMethods(self):
        return []

    def getProtectedAsyncMethods(self):
        return []

    def getPrivateMethods(self):
        return []

    def getPrivateSyncMethods(self):
        return []

    def getPrivateAsyncMethods(self):
        return []

    def getPublicClassMethods(self):
        return []

    def getPublicClassSyncMethods(self):
        return []

    def getPublicClassAsyncMethods(self):
        return []

    def getProtectedClassMethods(self):
        return []

    def getProtectedClassSyncMethods(self):
        return []

    def getProtectedClassAsyncMethods(self):
        return []

    def getPrivateClassMethods(self):
        return []

    def getPrivateClassSyncMethods(self):
        return []

    def getPrivateClassAsyncMethods(self):
        return []

    def getPublicStaticMethods(self):
        return []

    def getPublicStaticSyncMethods(self):
        return []

    def getPublicStaticAsyncMethods(self):
        return []

    def getProtectedStaticMethods(self):
        return []

    def getProtectedStaticSyncMethods(self):
        return []

    def getProtectedStaticAsyncMethods(self):
        return []

    def getPrivateStaticMethods(self):
        return []

    def getPrivateStaticSyncMethods(self):
        return []

    def getPrivateStaticAsyncMethods(self):
        return []

    def getDunderMethods(self):
        return []

    def getMagicMethods(self):
        return []

    def getProperties(self):
        return []

    def getPublicProperties(self):
        return []

    def getProtectedProperties(self):
        return []

    def getPrivateProperties(self):
        return []

    def getProperty(self, name):
        return None

    def getPropertySignature(self, name):
        return inspect.signature(lambda: None)

    def getPropertyDocstring(self, name):
        return ""

    def constructorSignature(self):
        return None

    def methodSignature(self, method_name):
        return None

    def clearCache(self):
        return None

class _OnlyGetInstance(IReflectionInstance):
    """
    Partial stub that implements only getInstance.

    Used to verify that attempting to instantiate a class that leaves
    the remaining abstract methods unimplemented raises TypeError.
    """

    def getInstance(self):
        return object()

class TestIReflectionInstanceIsABC(TestCase):

    def testIsABC(self) -> None:
        """
        Assert that IReflectionInstance inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IReflectionInstance, ABC))

    def testDirectInstantiationRaisesTypeError(self) -> None:
        """
        Assert that direct instantiation of IReflectionInstance raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IReflectionInstance()

    def testStubCanBeInstantiated(self) -> None:
        """
        Assert that a complete stub implementation can be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        stub = _StubInstance()
        self.assertIsInstance(stub, IReflectionInstance)

class TestIReflectionInstanceAbstractMethods(TestCase):

    def _assertAbstract(self, name: str) -> None:
        self.assertIn(name, IReflectionInstance.__abstractmethods__)

    def testGetInstanceIsAbstract(self) -> None:
        """
        Assert that getInstance is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getInstance")

    def testGetClassIsAbstract(self) -> None:
        """
        Assert that getClass is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getClass")

    def testGetClassNameIsAbstract(self) -> None:
        """
        Assert that getClassName is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getClassName")

    def testGetModuleNameIsAbstract(self) -> None:
        """
        Assert that getModuleName is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getModuleName")

    def testGetModuleWithClassNameIsAbstract(self) -> None:
        """
        Assert that getModuleWithClassName is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getModuleWithClassName")

    def testGetDocstringIsAbstract(self) -> None:
        """
        Assert that getDocstring is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getDocstring")

    def testGetBaseClassesIsAbstract(self) -> None:
        """
        Assert that getBaseClasses is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getBaseClasses")

    def testGetSourceCodeIsAbstract(self) -> None:
        """
        Assert that getSourceCode is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getSourceCode")

    def testGetFileIsAbstract(self) -> None:
        """
        Assert that getFile is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getFile")

    def testGetAnnotationsIsAbstract(self) -> None:
        """
        Assert that getAnnotations is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getAnnotations")

    def testHasAttributeIsAbstract(self) -> None:
        """
        Assert that hasAttribute is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("hasAttribute")

    def testGetAttributeIsAbstract(self) -> None:
        """
        Assert that getAttribute is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getAttribute")

    def testSetAttributeIsAbstract(self) -> None:
        """
        Assert that setAttribute is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("setAttribute")

    def testRemoveAttributeIsAbstract(self) -> None:
        """
        Assert that removeAttribute is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("removeAttribute")

    def testGetAttributesIsAbstract(self) -> None:
        """
        Assert that getAttributes is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getAttributes")

    def testGetPublicAttributesIsAbstract(self) -> None:
        """
        Assert that getPublicAttributes is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicAttributes")

    def testGetProtectedAttributesIsAbstract(self) -> None:
        """
        Assert that getProtectedAttributes is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedAttributes")

    def testGetPrivateAttributesIsAbstract(self) -> None:
        """
        Assert that getPrivateAttributes is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateAttributes")

    def testGetDunderAttributesIsAbstract(self) -> None:
        """
        Assert that getDunderAttributes is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getDunderAttributes")

    def testGetMagicAttributesIsAbstract(self) -> None:
        """
        Assert that getMagicAttributes is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getMagicAttributes")

    def testHasMethodIsAbstract(self) -> None:
        """
        Assert that hasMethod is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("hasMethod")

    def testSetMethodIsAbstract(self) -> None:
        """
        Assert that setMethod is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("setMethod")

    def testRemoveMethodIsAbstract(self) -> None:
        """
        Assert that removeMethod is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("removeMethod")

    def testGetMethodSignatureIsAbstract(self) -> None:
        """
        Assert that getMethodSignature is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getMethodSignature")

    def testGetMethodDocstringIsAbstract(self) -> None:
        """
        Assert that getMethodDocstring is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getMethodDocstring")

    def testGetMethodsIsAbstract(self) -> None:
        """
        Assert that getMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getMethods")

    def testGetPublicMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicMethods")

    def testGetPublicSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicSyncMethods")

    def testGetPublicAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicAsyncMethods")

    def testGetProtectedMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedMethods")

    def testGetProtectedSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedSyncMethods")

    def testGetProtectedAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedAsyncMethods")

    def testGetPrivateMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateMethods")

    def testGetPrivateSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateSyncMethods")

    def testGetPrivateAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateAsyncMethods")

    def testGetPublicClassMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicClassMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicClassMethods")

    def testGetPublicClassSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicClassSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicClassSyncMethods")

    def testGetPublicClassAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicClassAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicClassAsyncMethods")

    def testGetProtectedClassMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedClassMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedClassMethods")

    def testGetProtectedClassSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedClassSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedClassSyncMethods")

    def testGetProtectedClassAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedClassAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedClassAsyncMethods")

    def testGetPrivateClassMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateClassMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateClassMethods")

    def testGetPrivateClassSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateClassSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateClassSyncMethods")

    def testGetPrivateClassAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateClassAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateClassAsyncMethods")

    def testGetPublicStaticMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicStaticMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicStaticMethods")

    def testGetPublicStaticSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicStaticSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicStaticSyncMethods")

    def testGetPublicStaticAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPublicStaticAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicStaticAsyncMethods")

    def testGetProtectedStaticMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedStaticMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedStaticMethods")

    def testGetProtectedStaticSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedStaticSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedStaticSyncMethods")

    def testGetProtectedStaticAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getProtectedStaticAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedStaticAsyncMethods")

    def testGetPrivateStaticMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateStaticMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateStaticMethods")

    def testGetPrivateStaticSyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateStaticSyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateStaticSyncMethods")

    def testGetPrivateStaticAsyncMethodsIsAbstract(self) -> None:
        """
        Assert that getPrivateStaticAsyncMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateStaticAsyncMethods")

    def testGetDunderMethodsIsAbstract(self) -> None:
        """
        Assert that getDunderMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getDunderMethods")

    def testGetMagicMethodsIsAbstract(self) -> None:
        """
        Assert that getMagicMethods is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getMagicMethods")

    def testGetPropertiesIsAbstract(self) -> None:
        """
        Assert that getProperties is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProperties")

    def testGetPublicPropertiesIsAbstract(self) -> None:
        """
        Assert that getPublicProperties is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPublicProperties")

    def testGetProtectedPropertiesIsAbstract(self) -> None:
        """
        Assert that getProtectedProperties is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProtectedProperties")

    def testGetPrivatePropertiesIsAbstract(self) -> None:
        """
        Assert that getPrivateProperties is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPrivateProperties")

    def testGetPropertyIsAbstract(self) -> None:
        """
        Assert that getProperty is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getProperty")

    def testGetPropertySignatureIsAbstract(self) -> None:
        """
        Assert that getPropertySignature is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPropertySignature")

    def testGetPropertyDocstringIsAbstract(self) -> None:
        """
        Assert that getPropertyDocstring is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("getPropertyDocstring")

    def testConstructorSignatureIsAbstract(self) -> None:
        """
        Assert that constructorSignature is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("constructorSignature")

    def testMethodSignatureIsAbstract(self) -> None:
        """
        Assert that methodSignature is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("methodSignature")

    def testClearCacheIsAbstract(self) -> None:
        """
        Assert that clearCache is an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self._assertAbstract("clearCache")

class TestIReflectionInstancePartialImplementation(TestCase):

    def testPartialImplementationRaisesTypeError(self) -> None:
        """
        Assert that instantiating a class with only one method implemented raises
        TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _OnlyGetInstance()

class TestIReflectionInstanceStubReturnTypes(TestCase):

    def setUp(self) -> None:
        """
        Instantiate the stub before each test.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.stub = _StubInstance()

    def testGetInstanceReturnsObject(self) -> None:
        """
        Assert that getInstance returns an object instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getInstance(), object)

    def testGetClassReturnsType(self) -> None:
        """
        Assert that getClass returns a type object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getClass(), type)

    def testGetClassNameReturnsStr(self) -> None:
        """
        Assert that getClassName returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getClassName(), str)

    def testGetModuleNameReturnsStr(self) -> None:
        """
        Assert that getModuleName returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getModuleName(), str)

    def testGetModuleWithClassNameReturnsStr(self) -> None:
        """
        Assert that getModuleWithClassName returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getModuleWithClassName(), str)

    def testGetDocstringReturnsNoneOrStr(self) -> None:
        """
        Assert that getDocstring returns None or a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = self.stub.getDocstring()
        self.assertTrue(result is None or isinstance(result, str))

    def testGetBaseClassesReturnsTuple(self) -> None:
        """
        Assert that getBaseClasses returns a tuple.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getBaseClasses(), tuple)

    def testGetAnnotationsReturnsDict(self) -> None:
        """
        Assert that getAnnotations returns a dictionary.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getAnnotations(), dict)

    def testGetMethodsReturnsList(self) -> None:
        """
        Assert that getMethods returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getMethods(), list)

    def testGetPropertiesReturnsList(self) -> None:
        """
        Assert that getProperties returns a list.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsInstance(self.stub.getProperties(), list)

    def testClearCacheReturnsNone(self) -> None:
        """
        Assert that clearCache returns None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIsNone(self.stub.clearCache())
