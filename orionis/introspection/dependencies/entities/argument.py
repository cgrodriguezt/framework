from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, kw_only=True)
class Argument:
    """
    Represent a function or method argument with type and resolution metadata.

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
    type : type[Any]
        The Python type object for the argument's type.
    full_class_path : str
        The complete dotted path to the argument's type (module.class).
    is_keyword_only : bool, optional
        Indicates if the argument is keyword-only (default is False).
    is_schema : bool, optional
        Indicates if the argument is a schema (default is False).
    default : Any | None, optional
        The default value of the argument, if any (default is None).
    """

    # Required identification and type-resolution fields.
    name: str
    resolved: bool
    module_name: str
    class_name: str
    type: type[Any]
    full_class_path: str

    # Optional metadata fields with sensible defaults.
    is_keyword_only: bool = False
    is_schema: bool = False
    default: Any | None = None
