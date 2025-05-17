"""
This module overrides Python's built-in import mechanism to track and log
the number of times modules from the 'orionis' package are imported.
It prints a message each time such a module is imported, including the import count
and the fromlist used.

Usage:
    Simply import this module at the start of your application to enable tracking.
"""

import builtins
from collections import defaultdict
from threading import Lock

# Store the original __import__ function
_original_import = builtins.__import__

# Dictionary to count imports per module
_import_count = defaultdict(int)

# Lock to ensure thread safety
_import_lock = Lock()

def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Custom import function that tracks imports of 'orionis' modules.

    Args:
        name (str): The name of the module to import.
        globals (dict, optional): The global namespace.
        locals (dict, optional): The local namespace.
        fromlist (tuple, optional): Names to import from the module.
        level (int, optional): Relative import level.

    Returns:
        The imported module.
    """
    if str(name).startswith("orionis"):
        with _import_lock:
            _import_count[name] += 1
            count = _import_count[name]
        print(
            f"\033[2m\033[1mModule:\033[0m\033[2m '{name}' | "
            f"\033[1mImport Count:\033[0m\033[2m {count} | "
            f"\033[1mFromList:\033[0m\033[2m {fromlist}\033[0m"
        )
    return _original_import(name, globals, locals, fromlist, level)

# Override the built-in __import__ function
builtins.__import__ = custom_import