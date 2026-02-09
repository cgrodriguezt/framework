from __future__ import annotations
import ast
import importlib
import inspect
import sys
import warnings
from typing import Any, ClassVar

warnings.simplefilter("always", DeprecationWarning)

class TypeCheckingResolver:

    _cache: ClassVar[dict[str, dict[str, Any]]] = {}
    _source_cache: ClassVar[dict[str, str | None]] = {}

    @classmethod
    def fromModule(cls, module_name: str) -> dict[str, Any]:
        """
        Retrieve symbols imported in TYPE_CHECKING blocks from a module.

        Parameters
        ----------
        module_name : str
            Name of the module to inspect for TYPE_CHECKING imports.

        Returns
        -------
        dict[str, Any]
            Dictionary mapping symbol names to their imported objects.
        """
        warnings.warn(
            "\n" + "*" * 80 + "\n"
            "🚨 DEPRECATION ALERT 🚨\n"
            "The TypeCheckingResolver class is deprecated since Orionis beta.\n"
            "Using this class may impact performance and is not recommended.\n"
            "Recommendation: import types directly instead of using TYPE_CHECKING.\n"
            "*" * 80 + "\n",
            DeprecationWarning,
            stacklevel=2,
        )

        # Return cached result if available for performance
        cached_result: dict[str, Any] | None = cls._cache.get(module_name)
        if cached_result is not None:
            return cached_result

        # Get module source with caching
        source: str | None = cls._getModuleSource(module_name)
        if source is None:
            # Cache empty result to avoid repeated failed lookups
            empty_result: dict[str, Any] = {}
            cls._cache[module_name] = empty_result
            return empty_result

        try:
            # Parse AST and extract TYPE_CHECKING imports
            tree: ast.Module = ast.parse(source)
            symbols: dict[str, Any] = cls._extractTypeCheckingImports(tree)
        except SyntaxError:
            # Handle malformed source gracefully
            empty_result: dict[str, Any] = {}
            cls._cache[module_name] = empty_result
            return empty_result

        # Cache and return the result
        cls._cache[module_name] = symbols
        return symbols

    @classmethod
    def _getModuleSource(cls, module_name: str) -> str | None:
        """
        Retrieve the source code of a module and cache the result.

        Parameters
        ----------
        module_name : str
            Name of the module to retrieve source code from.

        Returns
        -------
        str | None
            Source code of the module if available, otherwise None.

        Notes
        -----
        Uses inspect.getsource for retrieval and caches results for performance.
        """
        # Check cache for previously retrieved source
        if module_name in cls._source_cache:
            return cls._source_cache[module_name]

        # Retrieve module from sys.modules to avoid unnecessary import
        module = sys.modules.get(module_name)
        if module is None:
            cls._source_cache[module_name] = None
            return None

        try:
            # Attempt to get source code using inspect
            source: str = inspect.getsource(module)
            cls._source_cache[module_name] = source
            return source
        except (OSError, TypeError):
            # Cache None to prevent repeated failed attempts
            cls._source_cache[module_name] = None
            return None

    @classmethod
    def _extractTypeCheckingImports(
        cls, tree: ast.Module,
    ) -> dict[str, Any]:
        """
        Extract import statements from TYPE_CHECKING blocks in the AST.

        Parameters
        ----------
        tree : ast.Module
            Parsed AST tree of the module to inspect.

        Returns
        -------
        dict[str, Any]
            Dictionary mapping symbol names to imported objects.

        Notes
        -----
        Only top-level TYPE_CHECKING blocks are processed.
        """
        result: dict[str, Any] = {}

        # Iterate over top-level nodes to find TYPE_CHECKING blocks
        for node in tree.body:
            if cls._isTypeCheckingIf(node):
                # Extract imports from the TYPE_CHECKING block
                cls._processTypeCheckingBlock(node.body, result)

        return result

    @staticmethod
    def _isTypeCheckingIf(node: ast.AST) -> bool:
        """
        Identify if an AST node is an 'if TYPE_CHECKING:' block.

        Parameters
        ----------
        node : ast.AST
            AST node to inspect for TYPE_CHECKING pattern.

        Returns
        -------
        bool
            True if node is an 'if TYPE_CHECKING:' block, otherwise False.

        Notes
        -----
        Checks for ast.If node with test as ast.Name and id 'TYPE_CHECKING'.
        """
        # Fast path: check instance type first for performance
        if not isinstance(node, ast.If):
            return False

        # Check if test is a Name node with TYPE_CHECKING identifier
        return (
            isinstance(node.test, ast.Name) and
            node.test.id == "TYPE_CHECKING"
        )

    @staticmethod
    def _processTypeCheckingBlock(
        body: list[ast.stmt], output: dict[str, Any],
    ) -> None:
        """
        Process TYPE_CHECKING block body and extract import statements.

        Parameters
        ----------
        body : list[ast.stmt]
            AST statements within the TYPE_CHECKING block.
        output : dict[str, Any]
            Dictionary to populate with imported symbols.

        Returns
        -------
        None
            Modifies the output dictionary in-place with found symbols.

        Notes
        -----
        Handles both 'import' and 'from ... import ...' statements.
        """
        # Iterate through statements and handle import types
        for stmt in body:
            if isinstance(stmt, ast.ImportFrom):
                TypeCheckingResolver._handleImportFrom(stmt, output)
            elif isinstance(stmt, ast.Import):
                TypeCheckingResolver._handleImport(stmt, output)

    @staticmethod
    def _handleImportFrom(
        node: ast.ImportFrom, output: dict[str, Any],
    ) -> None:
        """
        Handle 'from module import symbol' statements in TYPE_CHECKING blocks.

        Parameters
        ----------
        node : ast.ImportFrom
            AST node representing the import-from statement.
        output : dict[str, Any]
            Dictionary to populate with imported symbols.

        Returns
        -------
        None
            Modifies output dictionary in-place with resolved symbols.

        Notes
        -----
        Imports symbols from the specified module and adds them to the output
        dictionary. Skips modules that cannot be imported or symbols that do not
        exist in the module.
        """
        module_path: str | None = node.module
        if module_path is None:
            # Skip imports without module specification
            return

        try:
            # Import the target module
            imported_module = importlib.import_module(module_path)
        except (ImportError, ModuleNotFoundError):  # NOSONAR
            # Silently ignore unavailable modules
            return

        # Extract each imported symbol and add to output dictionary
        for alias in node.names:
            symbol_name: str = alias.name
            if hasattr(imported_module, symbol_name):
                symbol = getattr(imported_module, symbol_name)
                output_name: str = alias.asname or symbol_name
                output[output_name] = symbol

    @staticmethod
    def _handleImport(node: ast.Import, output: dict[str, Any]) -> None:
        """
        Process 'import module' statements found in TYPE_CHECKING blocks.

        Parameters
        ----------
        node : ast.Import
            AST node representing the import statement.
        output : dict[str, Any]
            Dictionary to populate with imported modules.

        Returns
        -------
        None
            Updates the output dictionary in-place with imported modules.

        Notes
        -----
        Each module is imported and added to the output dictionary using its alias
        or original name. Modules that cannot be imported are skipped.
        """
        # Iterate through each module specified in the import statement
        for alias in node.names:
            module_name: str = alias.name
            try:
                imported_module = importlib.import_module(module_name)
                output_name: str = alias.asname or module_name
                output[output_name] = imported_module
            except (ImportError, ModuleNotFoundError):  # NOSONAR
                # Skip modules that cannot be imported
                continue
