from __future__ import annotations
import ast
import sys
import inspect
import importlib
from typing import Any, ClassVar

class TypeCheckingResolver:

    _cache: ClassVar[dict[str, dict[str, Any]]] = {}
    _source_cache: ClassVar[dict[str, str | None]] = {}

    @classmethod
    def fromModule(cls, module_name: str) -> dict[str, Any]:
        """Retrieve symbols imported in TYPE_CHECKING blocks from a module.

        Parameters
        ----------
        module_name : str
            Name of the module to inspect for TYPE_CHECKING imports.

        Returns
        -------
        dict[str, Any]
            Dictionary mapping symbol names to their imported objects.
        """
        # Return cached result if available for performance
        cached_result = cls._cache.get(module_name)
        if cached_result is not None:
            return cached_result

        # Get module source with caching
        source = cls._getModuleSource(module_name)
        if source is None:
            # Cache empty result to avoid repeated failed lookups
            empty_result: dict[str, Any] = {}
            cls._cache[module_name] = empty_result
            return empty_result

        try:
            # Parse AST and extract TYPE_CHECKING imports
            tree = ast.parse(source)
            symbols = cls._extractTypeCheckingImports(tree)
        except SyntaxError:
            # Handle malformed source gracefully
            empty_result = {}
            cls._cache[module_name] = empty_result
            return empty_result

        # Cache and return the result
        cls._cache[module_name] = symbols
        return symbols

    @classmethod
    def _getModuleSource(cls, module_name: str) -> str | None:
        """Retrieve the source code of a module with caching.

        Parameters
        ----------
        module_name : str
            Name of the module to retrieve source code from.

        Returns
        -------
        str | None
            Source code of the module, or None if unavailable.
        """
        # Check source cache first for performance
        if module_name in cls._source_cache:
            return cls._source_cache[module_name]

        # Get module from sys.modules to avoid import overhead
        module = sys.modules.get(module_name)
        if module is None:
            cls._source_cache[module_name] = None
            return None

        try:
            # Extract source code using inspect
            source = inspect.getsource(module)
            cls._source_cache[module_name] = source
            return source
        except (OSError, TypeError):
            # Cache None result to avoid repeated failed attempts
            cls._source_cache[module_name] = None
            return None

    @classmethod
    def _extractTypeCheckingImports(cls, tree: ast.Module) -> dict[str, Any]:
        """Extract import statements from TYPE_CHECKING blocks in AST.

        Parameters
        ----------
        tree : ast.Module
            The parsed AST tree of the module to inspect.

        Returns
        -------
        dict[str, Any]
            Dictionary mapping symbol names to imported objects.
        """
        result: dict[str, Any] = {}

        # Process only top-level nodes for TYPE_CHECKING blocks
        for node in tree.body:
            if cls._isTypeCheckingIf(node):
                # Extract imports from the TYPE_CHECKING block
                cls._processTypeCheckingBlock(node.body, result)

        return result

    @staticmethod
    def _isTypeCheckingIf(node: ast.AST) -> bool:
        """Determine if AST node represents 'if TYPE_CHECKING:' block.

        Parameters
        ----------
        node : ast.AST
            The AST node to inspect for TYPE_CHECKING pattern.

        Returns
        -------
        bool
            True if node is 'if TYPE_CHECKING:' block, False otherwise.
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
        """Process and extract imports from TYPE_CHECKING block body.

        Parameters
        ----------
        body : list[ast.stmt]
            List of AST statements within the TYPE_CHECKING block.
        output : dict[str, Any]
            Dictionary to populate with imported symbols.

        Returns
        -------
        None
            Modifies output dictionary in-place with found symbols.
        """
        # Process each statement in the TYPE_CHECKING block
        for stmt in body:
            # Handle different types of import statements efficiently
            if isinstance(stmt, ast.ImportFrom):
                TypeCheckingResolver._handleImportFrom(stmt, output)
            elif isinstance(stmt, ast.Import):
                TypeCheckingResolver._handleImport(stmt, output)

    @staticmethod
    def _handleImportFrom(
        node: ast.ImportFrom, output: dict[str, Any],
    ) -> None:
        """Handle 'from module import symbol' statements from TYPE_CHECKING.

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
        """
        module_path = node.module
        if not module_path:
            # Skip imports without module specification
            return

        try:
            # Import the target module
            imported_module = importlib.import_module(module_path)
        except (ImportError, ModuleNotFoundError): # NOSONAR
            # Silently ignore unavailable modules
            return

        # Extract each imported symbol with optimized attribute check
        for alias in node.names:
            symbol_name = alias.name
            # Performance: Check attribute existence before getattr
            if hasattr(imported_module, symbol_name):
                symbol = getattr(imported_module, symbol_name)
                # Use alias name if provided, otherwise use original name
                output_name = alias.asname or symbol_name
                output[output_name] = symbol

    @staticmethod
    def _handleImport(node: ast.Import, output: dict[str, Any]) -> None:
        """Process 'import module' statements from TYPE_CHECKING blocks.

        Parameters
        ----------
        node : ast.Import
            AST node representing the import statement.
        output : dict[str, Any]
            Dictionary to populate with imported modules.

        Returns
        -------
        None
            Modifies output dictionary in-place with imported modules.
        """
        # Process each imported module in the statement
        for alias in node.names:
            module_name = alias.name
            try:
                # Import the module and store with appropriate name
                imported_module = importlib.import_module(module_name)
                output_name = alias.asname or module_name
                output[output_name] = imported_module
            except (ImportError, ModuleNotFoundError): # NOSONAR
                # Skip modules that cannot be imported
                continue
