from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, kw_only=True)
class Argument:
    """
    Represent a function or method argument with type information and resolution status.

    Parameters
    ----------
    name : str
        The name of the argument.
    resolved : bool
        Indicates whether the argument has been resolved or processed.
    module_name : str
        The module where the argument's type is defined.
    class_name : str
        The class representing the argument's type.
    type : Type[Any]
        The Python type object for the argument's type.
    full_class_path : str
        The complete dotted path to the argument's type (module.class).
    is_keyword_only : bool, optional
        Indicates if the argument is keyword-only (default is False).
    is_schema : bool, optional
        Indicates if the argument is a schema (default is False).
    default : Any | None, optional
        The default value of the argument, if any (default is None).

    Returns
    -------
    Argument
        An instance representing the argument metadata.
    """

    name: str
    resolved: bool
    module_name: str
    class_name: str
    type: type[Any]
    full_class_path: str
    is_keyword_only: bool = False
    is_schema: bool = False
    default: Any | None = None
