from __future__ import annotations
import ast
import importlib
import inspect
import re
from dataclasses import is_dataclass
from pathlib import Path
import sys
from typing import Any

class ModuleEngine:

    # ruff: noqa: PERF203, RUF012

    # Caches for discovered modules and resolved classes
    __cache_modules: set[str] = set()
    __cache_resolved_classes: dict[str, type] = {}

    @staticmethod
    def scan(
        app_root: Path,
        tarjet_path: Path,
    ) -> set[str]:
        """
        Discover Python modules.

        Traverse the target_path to find Python files and convert their paths to
        module notation. Cleans up paths to exclude virtual environment and
        site-packages directories.

        Parameters
        ----------
        app_root : Path
            The root directory of the application.
        tarjet_path : Path
            The target directory to search for Python modules.

        Returns
        -------
        set of str
            A set containing discovered module names in dot notation.
        """
        # Set to hold discovered module names
        modules: set[str] = set()

        # Recursively search for all .py files in tarjet_path
        for file_path in tarjet_path.rglob("*.py"):
            if not file_path.is_file():
                continue

            # Convert absolute path to module notation relative to app_root
            pre_module = (
                file_path.parent.as_posix()
                .replace(app_root.as_posix(), "")
                .replace("/", ".")
                .lstrip(".")
            )

            # Remove site-packages and virtual environment directories
            pre_module = re.sub(
                r"[^.]*\.(?:Lib|lib)\.(?:python[^.]*\.)?site-packages\.?",
                "",
                pre_module,
            )
            pre_module = re.sub(r"\.?v?env\.?", "", pre_module)

            # Remove redundant dots
            pre_module = re.sub(r"\.+", ".", pre_module).strip(".")

            # Skip if pre_module is empty after cleanup
            if not pre_module:
                continue

            # Add the complete module name to the set
            modules.add(f"{pre_module}.{file_path.stem}")

        # Return the set of discovered modules
        return modules

    @classmethod
    def resolveClass(
        cls,
        module_path: str | None = None,
        class_name: str | None = None,
        *,
        metadata: dict[str, str] | None = None,
    ) -> type:
        """
        Resolve and return a class object from a module.

        Import the specified module and retrieve the class by name, using
        internal caches for efficiency.

        Parameters
        ----------
        module_path : str
            Dotted path to the module (e.g., 'orionis.*.config.app.entities.app').
        class_name : str
            Name of the class to retrieve from the module.
        metadata : dict[str, str], optional
            Optional metadata containing 'module' and 'class' keys to specify

        Returns
        -------
        type
            The resolved class object.

        Raises
        ------
        ImportError
            If the module cannot be imported.
        AttributeError
            If the class does not exist in the module.
        TypeError
            If the resolved attribute is not a class.
        """
        # If metadata is provided, extract module and class names
        if (
            metadata is not None and
            isinstance(metadata, dict) and
            metadata and
            module_path is None and
            class_name is None
        ):
            module_path = metadata.get("module")
            class_name = metadata.get("class")

        # Use the fully qualified class name as the cache key
        class_key = f"{module_path}.{class_name}"

        # Return the cached class if already resolved
        if class_key in cls.__cache_resolved_classes:
            return cls.__cache_resolved_classes[class_key]

        # Use module cache to avoid re-importing
        if module_path not in cls.__cache_modules:
            try:
                module = importlib.import_module(module_path)
                cls.__cache_modules.add(module_path)
            except ImportError as e:
                error_msg = f"Could not import module '{module_path}': {e}"
                raise ImportError(error_msg) from e
        else:
            module = sys.modules[module_path]

        # Attempt to retrieve the class from the module
        try:
            klass = getattr(module, class_name)
        except AttributeError as e:
            error_msg = (
                f"Module '{module_path}' does not have a class "
                f"'{class_name}': {e}"
            )
            raise AttributeError(error_msg) from e

        # Ensure the resolved attribute is a class
        if not isinstance(klass, type):
            error_msg = (
                f"Attribute '{class_name}' in module '{module_path}' is not a "
                "class."
            )
            raise TypeError(error_msg)

        # Cache the resolved class for future calls
        cls.__cache_resolved_classes[class_key] = klass

        # Return the resolved class
        return klass

    @staticmethod
    def containsImports(
        file_path: Path,
        target_modules: set[str],
    ) -> bool:
        """
        Check if the file imports any of the target modules using AST analysis.

        Parameters
        ----------
        file_path : Path
            Path to the file to analyze.
        target_modules : set of str
            Set of module names to check for imports.

        Returns
        -------
        bool
            True if the file imports any of the target modules, otherwise False.
        """
        # Return False if the file does not exist
        if not file_path.is_file():
            return False

        try:
            # Parse the file content into an AST
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            return False

        # Helper to check for import statements matching target modules
        def is_target_import(node: ast.AST) -> bool:
            if isinstance(node, ast.ImportFrom):
                return node.module in target_modules
            if isinstance(node, ast.Import):
                return any(
                    alias.name in target_modules
                    for alias in node.names
                )
            return False

        # Walk the AST and check for matching imports
        return any(is_target_import(node) for node in ast.walk(tree))

    @staticmethod
    def discoverFinalDataclasses(
        modules: set[str],
    ) -> set[tuple[str, str, str, type[Any]]]:
        """
        Discover all frozen dataclasses in the given modules.

        Traverse the provided set of module names, import each module, and
        inspect its attributes to find dataclasses that are frozen (final).
        Only classes defined within the module are considered.

        Parameters
        ----------
        self : Any
            The instance or class reference (not used).
        modules : set[str]
            Set of module names to inspect.

        Returns
        -------
        set of tuple[str, str, str, type[Any]]
            A set of tuples containing the file name (without extension),
            module path, class name, and class type for each discovered
            frozen dataclass.
        """
        # Set to store discovered frozen dataclasses
        dataclasses: set[tuple[str, str, str, type[Any]]] = set()
        for module_path in modules:
            try:
                # Import the module dynamically
                module = importlib.import_module(module_path)
                for attr_name, attr in vars(module).items():
                    # Only consider classes defined in this module and are dataclasses
                    if (
                        inspect.isclass(attr)
                        and attr.__module__ == module.__name__
                        and is_dataclass(attr)
                    ):
                        dataclass_params = getattr(
                            attr,
                            "__dataclass_params__",
                            None,
                        )
                        # Check if the dataclass is frozen (final)
                        if (
                            dataclass_params
                            and getattr(dataclass_params, "frozen", False)
                        ):
                            # Extract the file name from the module's __file__ attribute
                            basename = Path(
                                getattr(module, "__file__", "unknown"),
                            ).name
                            # Get the file name without extension
                            file_name = Path(basename).stem
                            # Store the discovered frozen dataclass in the set
                            dataclasses.add(
                                (file_name, module_path, attr_name, attr),
                            )
            except Exception as e:
                # Raise a RuntimeError with a descriptive error message
                error_msg = f"Failed to import module {module_path}: {e!s}"
                raise RuntimeError(error_msg) from e

        # Return the set of discovered frozen dataclasses
        return dataclasses
