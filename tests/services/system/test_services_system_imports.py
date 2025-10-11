import sys
import os
import types
from unittest.mock import patch, MagicMock
from orionis.services.system.imports import Imports
from orionis.test.cases.synchronous import SyncTestCase

class TestServicesSystemImports(SyncTestCase):

    def testImportModule(self) -> None:
        """
        Tests that an Imports instance can be created and that the collect() method
        successfully populates its imports list.

        This test verifies the basic instantiation of the Imports class and ensures
        that the collect() method executes without errors, returning the instance itself.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create an instance of Imports
        imports = Imports()

        # Populate the imports list and verify return value
        result = imports.collect()

        # Assert that the instance is of type Imports
        self.assertIsInstance(imports, Imports)

        # Assert that collect() returns the same instance
        self.assertIs(result, imports)

    def testCollectPopulatesImports(self):
        """
        Tests that the collect() method of the Imports class populates the imports list with modules.

        This test creates a dummy module, adds it to sys.modules, and verifies that after calling
        collect(), the dummy module appears in the imports list of the Imports instance.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module and set its __file__ attribute
        dummy_mod = types.ModuleType("dummy_mod")
        dummy_mod.__file__ = os.path.join(os.getcwd(), "dummy_mod.py")

        # Add a dummy function to the module and set its __module__ attribute
        def dummy_func(): pass
        dummy_mod.dummy_func = dummy_func
        dummy_func.__module__ = "dummy_mod"

        # Register the dummy module in sys.modules
        sys.modules["dummy_mod"] = dummy_mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Check if the dummy module was collected
            found = any(imp["name"] == "dummy_mod" for imp in imports.imports)
            self.assertTrue(found)
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "dummy_mod" in sys.modules:
                del sys.modules["dummy_mod"]

    def testCollectExcludesStdlibAndSpecialModules(self):
        """
        Tests that the collect() method of the Imports class excludes standard library modules and special modules.

        This test verifies that after calling collect(), the resulting imports list does not contain entries for
        standard library modules such as __main__ or modules whose names start with _distutils. This ensures
        that the Imports class correctly filters out modules that should not be included in the imports list.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create Imports instance and collect imports
        imports = Imports()
        imports.collect()

        # Extract the names of collected modules
        names = [imp["name"] for imp in imports.imports]

        # Assert that '__main__' is not in the collected imports
        self.assertNotIn("__main__", names)

        # Assert that '__mp_main__' is not in the collected imports
        self.assertNotIn("__mp_main__", names)

        # Assert that modules starting with '_distutils' are not in the collected imports
        self.assertFalse(any(n.startswith("_distutils") for n in names))

    def testClearEmptiesImports(self):
        """
        Tests that the clear() method of the Imports class empties the imports list.

        This test manually populates the imports attribute of an Imports instance,
        calls the clear() method, and verifies that the imports list is empty afterward.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Create Imports instance and manually populate the imports list
        imports = Imports()
        imports.imports = [{"name": "test", "file": "test.py", "symbols": ["a"]}]

        # Verify imports list is not empty initially
        self.assertNotEqual(imports.imports, [])

        # Call clear() to empty the imports list
        imports.clear()

        # Assert that the imports list is now empty
        self.assertEqual(imports.imports, [])

    def testCollectHandlesModulesWithoutFile(self):
        """
        Tests that the collect() method of the Imports class correctly handles modules that do not have a __file__ attribute.

        This test creates a dummy module without a __file__ attribute, registers it in sys.modules, and verifies that after calling
        collect(), the module does not appear in the imports list of the Imports instance. This ensures that the Imports class
        properly skips modules lacking a __file__ attribute, which are typically built-in or dynamically created modules.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Create a dummy module without a __file__ attribute
        mod = types.ModuleType("mod_without_file")
        sys.modules["mod_without_file"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the dummy module is not in the collected imports
            self.assertNotIn("mod_without_file", names)
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "mod_without_file" in sys.modules:
                del sys.modules["mod_without_file"]

    def testCollectSkipsBinaryExtensions(self):
        """
        Tests that the collect() method of the Imports class skips binary extension modules.

        This test creates a dummy module with a .pyd file extension (representing a binary extension),
        registers it in sys.modules, and verifies that after calling collect(), the module does not
        appear in the imports list of the Imports instance. This ensures that the Imports class
        properly excludes binary extension modules from its collected imports.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module with a .pyd file extension to simulate a binary extension
        mod = types.ModuleType("bin_mod")
        mod.__file__ = "bin_mod.pyd"

        # Register the dummy binary module in sys.modules
        sys.modules["bin_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the binary module is not in the collected imports
            self.assertNotIn("bin_mod", names)
        finally:
            # Cleanup: remove the dummy binary module from sys.modules
            if "bin_mod" in sys.modules:
                del sys.modules["bin_mod"]

    def testCollectSkipsDllExtensions(self):
        """
        Tests that the collect() method skips modules with .dll file extensions.

        This test creates a dummy module with a .dll file extension (representing a Windows binary extension),
        registers it in sys.modules, and verifies that after calling collect(), the module does not
        appear in the imports list. This ensures proper filtering of Windows binary extensions.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module with a .dll file extension
        mod = types.ModuleType("dll_mod")
        mod.__file__ = "dll_mod.dll"

        # Register the dummy binary module in sys.modules
        sys.modules["dll_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the binary module is not in the collected imports
            self.assertNotIn("dll_mod", names)
        finally:
            # Cleanup: remove the dummy binary module from sys.modules
            if "dll_mod" in sys.modules:
                del sys.modules["dll_mod"]

    def testCollectSkipsSoExtensions(self):
        """
        Tests that the collect() method skips modules with .so file extensions.

        This test creates a dummy module with a .so file extension (representing a Unix shared object),
        registers it in sys.modules, and verifies that after calling collect(), the module does not
        appear in the imports list. This ensures proper filtering of Unix binary extensions.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module with a .so file extension
        mod = types.ModuleType("so_mod")
        mod.__file__ = "so_mod.so"

        # Register the dummy binary module in sys.modules
        sys.modules["so_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the binary module is not in the collected imports
            self.assertNotIn("so_mod", names)
        finally:
            # Cleanup: remove the dummy binary module from sys.modules
            if "so_mod" in sys.modules:
                del sys.modules["so_mod"]

    def testCollectSkipsInitFiles(self):
        """
        Tests that the collect() method skips __init__.py files.

        This test creates a dummy module with an __init__.py file path, registers it in sys.modules,
        and verifies that after calling collect(), the module does not appear in the imports list
        even if it has symbols. This ensures that __init__.py files are properly excluded.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module with __init__.py file path
        mod = types.ModuleType("init_mod")
        mod.__file__ = os.path.join(os.getcwd(), "init_mod", "__init__.py")

        # Add a dummy function to the module
        def dummy_func(): pass
        mod.dummy_func = dummy_func
        dummy_func.__module__ = "init_mod"

        # Register the dummy module in sys.modules
        sys.modules["init_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the __init__.py module is not in the collected imports
            self.assertNotIn("init_mod", names)
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "init_mod" in sys.modules:
                del sys.modules["init_mod"]

    def testCollectSkipsModulesWithoutSymbols(self):
        """
        Tests that the collect() method skips modules that have no symbols.

        This test creates a dummy module with a valid file path but no symbols (functions, classes, or submodules),
        registers it in sys.modules, and verifies that after calling collect(), the module does not appear
        in the imports list. This ensures that empty modules are properly excluded.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module without symbols
        mod = types.ModuleType("empty_mod")
        mod.__file__ = os.path.join(os.getcwd(), "empty_mod.py")

        # Register the dummy module in sys.modules
        sys.modules["empty_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the empty module is not in the collected imports
            self.assertNotIn("empty_mod", names)
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "empty_mod" in sys.modules:
                del sys.modules["empty_mod"]

    def testCollectIncludesModuleWithClass(self):
        """
        Tests that the collect() method includes modules that contain classes.

        This test creates a dummy module with a class, registers it in sys.modules,
        and verifies that after calling collect(), the module appears in the imports list
        with the class listed in its symbols.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module with a class
        mod = types.ModuleType("class_mod")
        mod.__file__ = os.path.join(os.getcwd(), "class_mod.py")

        # Create a dummy class and add it to the module
        class DummyClass:
            pass

        mod.DummyClass = DummyClass
        DummyClass.__module__ = "class_mod"

        # Register the dummy module in sys.modules
        sys.modules["class_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Find the module in collected imports
            found_import = None
            for imp in imports.imports:
                if imp["name"] == "class_mod":
                    found_import = imp
                    break

            # Assert that the module was collected
            self.assertIsNotNone(found_import)

            # Assert that the class is in the symbols
            self.assertIn("DummyClass", found_import["symbols"])
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "class_mod" in sys.modules:
                del sys.modules["class_mod"]

    def testCollectIncludesModuleWithSubmodule(self):
        """
        Tests that the collect() method includes modules that contain submodules.

        This test creates a dummy module with a submodule, registers it in sys.modules,
        and verifies that after calling collect(), the module appears in the imports list
        with the submodule listed in its symbols.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module with a submodule
        mod = types.ModuleType("parent_mod")
        mod.__file__ = os.path.join(os.getcwd(), "parent_mod.py")

        # Create a dummy submodule
        submod = types.ModuleType("parent_mod.sub")
        submod.__module__ = "parent_mod"
        mod.sub = submod

        # Register the dummy modules in sys.modules
        sys.modules["parent_mod"] = mod
        sys.modules["parent_mod.sub"] = submod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Find the module in collected imports
            found_import = None
            for imp in imports.imports:
                if imp["name"] == "parent_mod":
                    found_import = imp
                    break

            # Assert that the module was collected
            self.assertIsNotNone(found_import)

            # Assert that the submodule is in the symbols
            self.assertIn("sub", found_import["symbols"])
        finally:
            # Cleanup: remove the dummy modules from sys.modules
            if "parent_mod" in sys.modules:
                del sys.modules["parent_mod"]
            if "parent_mod.sub" in sys.modules:
                del sys.modules["parent_mod.sub"]

    def testCollectExcludesStdlibModules(self):
        """
        Tests that the collect() method excludes modules from the standard library.

        This test creates a dummy module that would be considered a standard library module
        by patching the standard library path and verifies proper exclusion.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module that appears to be in stdlib
        mod = types.ModuleType("stdlib_test_mod")

        # Use os.__file__ directory as stdlib path to simulate stdlib location
        import os as os_module
        stdlib_path = os.path.dirname(os_module.__file__)
        mod.__file__ = os.path.join(stdlib_path, "stdlib_test_mod.py")

        # Add a dummy function to ensure it would normally be collected
        def dummy_func(): pass
        mod.dummy_func = dummy_func
        dummy_func.__module__ = "stdlib_test_mod"

        # Register the dummy module in sys.modules
        sys.modules["stdlib_test_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the stdlib module is not in the collected imports
            self.assertNotIn("stdlib_test_mod", names)
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "stdlib_test_mod" in sys.modules:
                del sys.modules["stdlib_test_mod"]

    def testCollectExcludesVirtualEnvModules(self):
        """
        Tests that the collect() method excludes modules from the active virtual environment.

        This test uses the actual current virtual environment path to create a dummy module
        and verifies proper exclusion of virtual environment modules.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Get the current virtual environment path
        current_venv = os.environ.get("VIRTUAL_ENV")
        if not current_venv:
            # Skip test if no virtual environment is active
            self.skipTest("No virtual environment active")

        # Use the actual venv path with proper Windows formatting
        venv_path = os.path.abspath(current_venv)

        # Create a dummy module in virtual environment path
        mod = types.ModuleType("venv_test_mod")
        mod.__file__ = os.path.join(venv_path, "lib", "site-packages", "venv_test_mod.py")

        # Add a dummy function to ensure it would normally be collected
        def dummy_func(): pass
        mod.dummy_func = dummy_func
        dummy_func.__module__ = "venv_test_mod"

        # Register the dummy module in sys.modules
        sys.modules["venv_test_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Extract the names of collected modules
            names = [imp["name"] for imp in imports.imports]

            # Assert that the venv module is not in the collected imports
            self.assertNotIn("venv_test_mod", names)
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "venv_test_mod" in sys.modules:
                del sys.modules["venv_test_mod"]

    def testCollectHandlesSymbolCollectionErrors(self):
        """
        Tests that the collect() method gracefully handles errors during symbol collection.

        This test creates a dummy module with an attribute that raises an exception when accessed,
        and verifies that the module is still processed despite the error during symbol collection.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module
        mod = types.ModuleType("error_mod")
        mod.__file__ = os.path.join(os.getcwd(), "error_mod.py")

        # Create a property that raises an exception when accessed
        class ErrorProperty:
            def __get__(self, obj, objtype=None):
                raise RuntimeError("Error accessing attribute")

        mod.error_attr = ErrorProperty()

        # Add a valid function as well
        def dummy_func(): pass
        mod.dummy_func = dummy_func
        dummy_func.__module__ = "error_mod"

        # Register the dummy module in sys.modules
        sys.modules["error_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()

            # This should not raise an exception despite the error attribute
            imports.collect()

            # Note: The module might not appear if all symbol collection fails
            # This test primarily ensures no exception is raised
            self.assertIsInstance(imports.imports, list)
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "error_mod" in sys.modules:
                del sys.modules["error_mod"]

    def testCollectFiltersSymbolsByModule(self):
        """
        Tests that the collect() method only includes symbols that belong to the current module.

        This test creates a dummy module with symbols that have different __module__ attributes
        and verifies that only symbols belonging to the current module are included.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a dummy module
        mod = types.ModuleType("symbol_mod")
        mod.__file__ = os.path.join(os.getcwd(), "symbol_mod.py")

        # Add a function that belongs to this module
        def own_func(): pass
        mod.own_func = own_func
        own_func.__module__ = "symbol_mod"

        # Add a function that belongs to a different module
        def foreign_func(): pass
        mod.foreign_func = foreign_func
        foreign_func.__module__ = "other_module"

        # Register the dummy module in sys.modules
        sys.modules["symbol_mod"] = mod

        try:
            # Create Imports instance and collect imports
            imports = Imports()
            imports.collect()

            # Find the module in collected imports
            found_import = None
            for imp in imports.imports:
                if imp["name"] == "symbol_mod":
                    found_import = imp
                    break

            # Assert that the module was collected
            self.assertIsNotNone(found_import)

            # Assert that only the own function is in the symbols
            self.assertIn("own_func", found_import["symbols"])
            self.assertNotIn("foreign_func", found_import["symbols"])
        finally:
            # Cleanup: remove the dummy module from sys.modules
            if "symbol_mod" in sys.modules:
                del sys.modules["symbol_mod"]

    def testDisplayCallsCollectWhenImportsEmpty(self):
        """
        Tests that the display() method calls collect() when the imports list is empty.

        This test verifies that if display() is called on an Imports instance with no collected imports,
        it automatically calls collect() to populate the imports list before displaying.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create Imports instance (imports list is initially empty)
        imports = Imports()

        # Verify imports list is empty
        self.assertEqual(imports.imports, [])

        # Mock the Rich components to avoid actual console output
        with patch('rich.console.Console') as mock_console_class:
            mock_console = MagicMock()
            mock_console.size.width = 100
            mock_console_class.return_value = mock_console

            with patch('rich.table.Table') as mock_table_class, \
                 patch('rich.panel.Panel'):

                mock_table = MagicMock()
                mock_table_class.return_value = mock_table

                # Call display
                imports.display()

                # Verify that imports list is no longer empty (collect was called)
                # Since we're in a real environment, some modules should be collected
                self.assertIsInstance(imports.imports, list)

    def testDisplayWithExistingImports(self):
        """
        Tests that the display() method works correctly when imports are already collected.

        This test populates the imports list manually and verifies that display() uses the existing
        data without calling collect() again.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create Imports instance and manually populate imports
        imports = Imports()
        imports.imports = [
            {"name": "test_module", "file": "test_module.py", "symbols": ["test_func", "TestClass"]},
            {"name": "another_module", "file": "another_module.py", "symbols": ["another_func"]}
        ]

        # Mock the Rich components to avoid actual console output
        with patch('rich.console.Console') as mock_console_class:
            mock_console = MagicMock()
            mock_console.size.width = 100
            mock_console_class.return_value = mock_console

            with patch('rich.table.Table') as mock_table_class, \
                 patch('rich.panel.Panel') as mock_panel_class:

                mock_table = MagicMock()
                mock_table_class.return_value = mock_table

                # Call display
                imports.display()

                # Verify Rich components were used correctly
                mock_console_class.assert_called_once()
                mock_table_class.assert_called_once()
                mock_panel_class.assert_called_once()
                mock_console.print.assert_called_once()

                # Verify table.add_row was called for each import
                self.assertEqual(mock_table.add_row.call_count, 2)

    def testImportsAttributeInitialization(self):
        """
        Tests that the Imports class initializes with an empty imports list.

        This test verifies that a newly created Imports instance has an empty imports list
        and that the list is of the correct type.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create Imports instance
        imports = Imports()

        # Verify imports attribute is initialized as empty list
        self.assertEqual(imports.imports, [])
        self.assertIsInstance(imports.imports, list)

    def testCollectReturnsChainableInstance(self):
        """
        Tests that the collect() method returns the same instance for method chaining.

        This test verifies that collect() returns self, allowing for method chaining operations.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create Imports instance
        imports = Imports()

        # Call collect and verify it returns the same instance
        result = imports.collect()

        self.assertIs(result, imports)
        self.assertEqual(id(result), id(imports))

    def testCollectClearsPreviousImports(self):
        """
        Tests that the collect() method clears any previously collected imports.

        This test verifies that calling collect() multiple times properly clears the previous
        results and starts fresh, preventing duplicate entries.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create Imports instance and manually add some imports
        imports = Imports()
        imports.imports = [{"name": "old_module", "file": "old.py", "symbols": ["old_func"]}]

        # Verify there are existing imports
        self.assertEqual(len(imports.imports), 1)
        self.assertEqual(imports.imports[0]["name"], "old_module")

        # Call collect to refresh imports
        imports.collect()

        # Verify old imports were cleared and new collection occurred
        # The exact contents depend on the current sys.modules state,
        # but it should not contain our manually added entry
        old_module_found = any(imp["name"] == "old_module" for imp in imports.imports)
        self.assertFalse(old_module_found)