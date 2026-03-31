from __future__ import annotations
import tempfile
from pathlib import Path
from orionis.services.introspection.modules.inspector import ModuleInspector
from orionis.test import TestCase

# ===========================================================================
# TestModuleInspector
# ===========================================================================

class TestModuleInspector(TestCase):

    def testDiscoverModulesReturnsSet(self) -> None:
        """
        Assert that discoverModules returns a set.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = ModuleInspector.discoverModules(base, base)
        self.assertIsInstance(result, set)

    def testDiscoverModulesFindsFilesInDirectory(self) -> None:
        """
        Assert that discoverModules discovers .py files in a directory tree.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pkg = base / "mypkg"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("")
            (pkg / "module_a.py").write_text("")
            result = ModuleInspector.discoverModules(base, base)
        self.assertTrue(any("module_a" in m for m in result))

    def testDiscoverModulesReturnsEmptySetForEmptyDir(self) -> None:
        """
        Assert that discoverModules returns an empty set for an empty directory.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            result = ModuleInspector.discoverModules(base, base)
        self.assertEqual(result, set())

    def testLoadClassResolvesValidModule(self) -> None:
        """
        Assert that loadClass retrieves a class from a valid module.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        klass = ModuleInspector.loadClass(
            module_path="pathlib",
            class_name="Path",
        )
        self.assertIs(klass, Path)

    def testLoadClassRaisesImportErrorForInvalidModule(self) -> None:
        """
        Assert that loadClass raises ImportError for a non-existent module.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(ImportError):
            ModuleInspector.loadClass(
                module_path="non_existent_module_xyz_abc",
                class_name="SomeClass",
            )

    def testLoadClassRaisesAttributeErrorForInvalidClass(self) -> None:
        """
        Assert that loadClass raises AttributeError for a missing class name.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(AttributeError):
            ModuleInspector.loadClass(
                module_path="pathlib",
                class_name="NonExistentClass",
            )

    def testLoadClassUsesMetadataDict(self) -> None:
        """
        Assert that loadClass resolves from a metadata dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        klass = ModuleInspector.loadClass(
            metadata={"module": "pathlib", "class": "Path"},
        )
        self.assertIs(klass, Path)

    def testLoadClassCachesResolution(self) -> None:
        """
        Assert that loadClass returns the same object on subsequent calls.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        klass1 = ModuleInspector.loadClass(module_path="pathlib", class_name="Path")
        klass2 = ModuleInspector.loadClass(module_path="pathlib", class_name="Path")
        self.assertIs(klass1, klass2)

    def testFileImportsAnyReturnsFalseForNonExistentFile(self) -> None:
        """
        Assert that fileImportsAny returns False for a file that does not exist.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = ModuleInspector.fileImportsAny(
            file_path=Path("/nonexistent/file.py"),
            target_modules={"os"},
        )
        self.assertFalse(result)

    def testFileImportsAnyReturnsTrueWhenModuleIsImported(self) -> None:
        """
        Assert that fileImportsAny returns True when the file imports a target module.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("from pathlib import Path\n")
            tmp_path = Path(f.name)
        try:
            result = ModuleInspector.fileImportsAny(
                file_path=tmp_path,
                target_modules={"pathlib"},
            )
            self.assertTrue(result)
        finally:
            tmp_path.unlink(missing_ok=True)

    def testFileImportsAnyReturnsFalseWhenModuleNotImported(self) -> None:
        """
        Assert that fileImportsAny returns False when the file does not import the target.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("x = 1\n")
            tmp_path = Path(f.name)
        try:
            result = ModuleInspector.fileImportsAny(
                file_path=tmp_path,
                target_modules={"os", "sys"},
            )
            self.assertFalse(result)
        finally:
            tmp_path.unlink(missing_ok=True)
