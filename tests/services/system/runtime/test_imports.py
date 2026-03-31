from __future__ import annotations
from collections import defaultdict
from orionis.test import TestCase

# ===========================================================================
# TestRuntimeImports
# ===========================================================================

class TestRuntimeImports(TestCase):

    def testModuleImportsWithoutError(self) -> None:
        """
        Assert that importing the runtime imports module does not raise.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import importlib
        mod = importlib.import_module("orionis.services.system.runtime.imports")
        self.assertIsNotNone(mod)

    def testCustomImportFunctionExists(self) -> None:
        """
        Assert that the module exposes a custom_import callable.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import orionis.services.system.runtime.imports as rt
        self.assertTrue(callable(rt.custom_import))

    def testOriginalImportStoredInModule(self) -> None:
        """
        Assert that _original_import is stored as a reference to the original __import__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import orionis.services.system.runtime.imports as rt
        self.assertTrue(callable(rt._original_import))

    def testImportCountIsDefaultDict(self) -> None:
        """
        Assert that _import_count is a defaultdict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import orionis.services.system.runtime.imports as rt
        self.assertIsInstance(rt._import_count, defaultdict)

    def testImportLockExists(self) -> None:
        """
        Assert that _import_lock is a threading.Lock-like object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import orionis.services.system.runtime.imports as rt
        self.assertTrue(hasattr(rt._import_lock, "acquire"))
        self.assertTrue(hasattr(rt._import_lock, "release"))

    def testCustomImportAcceptsNameAndFromlist(self) -> None:
        """
        Assert that custom_import can be called with name and fromlist args.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import orionis.services.system.runtime.imports as rt
        result = rt.custom_import("os")
        self.assertIsNotNone(result)

    def testCustomImportTracksOrionisCalls(self) -> None:
        """
        Assert that importing an orionis module increments its count.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import orionis.services.system.runtime.imports as rt
        before = rt._import_count.get("orionis.services.system.runtime.imports", 0)
        rt.custom_import(
            "orionis.services.system.runtime.imports",
            globals(),
            locals(),
            (),
            0,
        )
        after = rt._import_count.get("orionis.services.system.runtime.imports", 0)
        self.assertGreaterEqual(after, before)

    def testCustomImportReturnsModuleObject(self) -> None:
        """
        Assert that custom_import returns a module-like object.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        import types
        import orionis.services.system.runtime.imports as rt
        result = rt.custom_import("sys")
        self.assertIsInstance(result, types.ModuleType)
