from __future__ import annotations
import inspect
from abc import ABC
from inspect import isabstract
from orionis.services.file.contracts.directory import IDirectory
from orionis.test import TestCase

class _ConcreteDirectory(IDirectory):
    """Minimal concrete implementation used to verify the contract."""

    def _stub_path(self):
        from pathlib import Path
        return Path("/stub")

    def root(self):           return self._stub_path()
    def app(self):            return self._stub_path()
    def console(self):        return self._stub_path()
    def exceptions(self):     return self._stub_path()
    def http(self):           return self._stub_path()
    def models(self):         return self._stub_path()
    def providers(self):      return self._stub_path()
    def notifications(self):  return self._stub_path()
    def services(self):       return self._stub_path()
    def jobs(self):           return self._stub_path()
    def bootstrap(self):      return self._stub_path()
    def config(self):         return self._stub_path()
    def database(self):       return self._stub_path()
    def resources(self):      return self._stub_path()
    def routes(self):         return self._stub_path()
    def storage(self):        return self._stub_path()
    def storagePublic(self):  return self._stub_path()
    def tests(self):          return self._stub_path()

class _PartialDirectory(IDirectory):
    """Subclass implementing only root — intentionally incomplete."""

    def root(self):
        from pathlib import Path
        return Path("/root")

# ===========================================================================
# TestIDirectoryContract
# ===========================================================================

class TestIDirectoryContract(TestCase):

    def testInheritsFromABC(self) -> None:
        """
        Assert that IDirectory inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IDirectory, ABC))

    def testIsAbstractClass(self) -> None:
        """
        Assert that inspect.isabstract identifies IDirectory as abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(isabstract(IDirectory))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating IDirectory directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IDirectory()  # type: ignore[abstract]

    def testExpectedAbstractMethodsExist(self) -> None:
        """
        Assert that all expected path methods are abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        expected = {
            "root", "app", "console", "exceptions", "http", "models",
            "providers", "notifications", "services", "jobs", "bootstrap",
            "config", "database", "resources", "routes", "storage",
            "storagePublic", "tests",
        }
        for method in expected:
            self.assertIn(method, IDirectory.__abstractmethods__, msg=f"'{method}' should be abstract")

    def testAbstractMethodsSetHasExpectedCount(self) -> None:
        """
        Assert that __abstractmethods__ contains exactly 18 methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(len(IDirectory.__abstractmethods__), 18)

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Assert that a subclass implementing only root cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _PartialDirectory()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Assert that a fully implemented subclass can be created without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteDirectory()
        self.assertIsInstance(instance, IDirectory)

    def testConcreteMethodsReturnPath(self) -> None:
        """
        Assert that each method in the concrete implementation returns a Path.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        from pathlib import Path
        instance = _ConcreteDirectory()
        methods = [
            "root", "app", "console", "exceptions", "http", "models",
            "providers", "notifications", "services", "jobs", "bootstrap",
            "config", "database", "resources", "routes", "storage",
            "storagePublic", "tests",
        ]
        for method in methods:
            result = getattr(instance, method)()
            self.assertIsInstance(result, Path, msg=f"{method}() should return Path")

    def testRootMethodSignature(self) -> None:
        """
        Assert that root method has a valid signature.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(IDirectory.root)
        self.assertIn("self", sig.parameters)
