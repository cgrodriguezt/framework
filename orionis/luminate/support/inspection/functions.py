from typing import Any, Type
import inspect
import importlib

def is_valid_module(module_name: str) -> bool:
    """Check if a module name is valid and can be imported.

    Parameters
    ----------
    module_name : str
        The name of the module to check

    Returns
    -------
    bool
        True if the module is valid and can be imported, False otherwise
    """
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def ensure_valid_module(module_name: str) -> None:
    """Ensure a module name is valid and can be imported.

    Parameters
    ----------
    module_name : str
        The name of the module to check

    Raises
    ------
    ValueError
        If the module cannot be imported or is invalid
    """
    if not isinstance(module_name, str):
        raise TypeError(f"Module name must be a string, got {type(module_name)}")
    if not is_valid_module(module_name):
        raise ValueError(f"Invalid or non-importable module: {module_name}")

def is_instantiable_class(cls: Type) -> bool:
    """Check if a class is concrete and can be instantiated.

    Parameters
    ----------
    cls : Type
        The class to check

    Returns
    --
    bool
        True if the class is concrete and can be instantiated, False otherwise
    """
    if not isinstance(cls, type):
        return False
    if is_abstract_class(cls):
        return False
    try:
        # Try to create an instance to verify it's truly concrete
        cls()
        return True
    except TypeError:
        return False

def ensure_instantiable_class(cls: Type) -> None:
    """Ensure a class is concrete and can be instantiated.

    Parameters
    ----------
    cls : Type
        The class to check

    Raises
    ------
    TypeError
        If the input is not a class
    ValueError
        If the class is abstract or cannot be instantiated
    """
    if not isinstance(cls, type):
        raise TypeError(f"Expected a class, got {type(cls)}")
    if is_abstract_class(cls):
        raise ValueError(f"Class '{cls.__name__}' is abstract")
    try:
        cls()
    except TypeError as e:
        raise ValueError(f"Class '{cls.__name__}' cannot be instantiated: {str(e)}")

def is_valid_class_name(module_name: str, class_name: str) -> bool:
    """Check if a class exists in a given module.

    Parameters
    ----------
    module_name : str
        The name of the module to check
    class_name : str
        The name of the class to look for

    Returns
    -------
    bool
        True if the class exists in the module, False otherwise
    """
    try:
        module = importlib.import_module(module_name)
        return hasattr(module, class_name) and inspect.isclass(getattr(module, class_name))
    except ImportError:
        return False

def ensure_valid_class_name(module_name: str, class_name: str) -> None:
    """Ensure a class exists in a given module.

    Parameters
    ----------
    module_name : str
        The name of the module to check
    class_name : str
        The name of the class to look for

    Raises
    ------
    ValueError
        If the class doesn't exist in the module
    """
    if not is_valid_class_name(module_name, class_name):
        raise ValueError(f"Class '{class_name}' not found in module '{module_name}'")

def is_user_defined_class_instance(instance: Any) -> bool:
    """Check if an object is an instance of a user-defined class.

    Parameters
    ----------
    instance : Any
        The object to check

    Returns
    -------
    bool
        True if the object is an instance of a user-defined class, False otherwise
    """
    return isinstance(instance, object) and type(instance).__module__ not in {'builtins', 'abc', '__main__'}

def ensure_user_defined_class_instance(instance: Any) -> None:
    """Ensure an object is an instance of a user-defined class.

    Parameters
    ----------
    instance : Any
        The object to check

    Raises
    ------
    TypeError
        If the input is not an object instance
    ValueError
        If the instance is from builtins, abc, or __main__
    """
    if not isinstance(instance, object):
        raise TypeError(f"Invalid object: {instance!r}")
    module = type(instance).__module__
    if module in {'builtins', 'abc'}:
        raise ValueError(f"'{instance!r}' is not a user-defined class instance, belongs to '{module}'.")
    if module == '__main__':
        raise ValueError("Instance originates from '__main__', origin indeterminate.")

def is_abstract_class(cls: Type) -> bool:
    """Check if a class is abstract.

    Parameters
    ----------
    cls : Type
        The class to check

    Returns
    -------
    bool
        True if the class is abstract, False otherwise
    """
    return isinstance(cls, type) and bool(getattr(cls, '__abstractmethods__', False))

def ensure_abstract_class(cls: Type) -> None:
    """Ensure a class is abstract.

    Parameters
    ----------
    cls : Type
        The class to check

    Raises
    ------
    TypeError
        If the input is not a class
    ValueError
        If the class is not abstract
    """
    if not isinstance(cls, type):
        raise TypeError(f"Invalid class: {cls!r}")
    if not is_abstract_class(cls):
        raise ValueError(f"Class '{cls.__name__}' is not abstract.")

def is_concrete_class(cls: Type) -> bool:
    """Check if a class is concrete.

    Parameters
    ----------
    cls : Type
        The class to check

    Returns
    -------
    bool
        True if the class is concrete, False otherwise
    """
    return isinstance(cls, type) and not is_abstract_class(cls)

def ensure_concrete_class(cls: Type) -> None:
    """Ensure a class is concrete.

    Parameters
    ----------
    cls : Type
        The class to check

    Raises
    ------
    TypeError
        If the input is not a class
    ValueError
        If the class is not concrete
    """
    if not isinstance(cls, type):
        raise TypeError(f"Invalid class: {cls!r}")
    if not is_concrete_class(cls):
        raise ValueError(f"Class '{cls.__name__}' is not concrete.")