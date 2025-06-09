from dataclasses import dataclass
import inspect
from typing import Any

@dataclass(frozen=True, kw_only=True)
class ClassProperty:
    """
    Represents a property of a class with its metadata.

    Parameters
    ----------
    name : str
        The name of the property.
    value : Any
        The value assigned to the property.
    signature : inspect.Signature
        The signature of the property, typically used for callable properties.
    doc : str
        The documentation string associated with the property.
    """
    name: str
    value: Any
    signature: inspect.Signature
    doc: str