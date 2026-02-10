from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, kw_only=True)
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
    default : Any | None, optional
        The default value of the argument, if any (default is None).

    Returns
    -------
    Argument
        An instance representing the argument metadata.

    Notes
    -----
    Validation is performed during initialization in __post_init__.
    """

    name: str
    resolved: bool
    module_name: str
    class_name: str
    type: type[Any]
    full_class_path: str
    is_keyword_only: bool = False
    default: Any | None = None

    def __post_init__(self) -> None:
        """
        Validate fields after initialization to ensure data integrity.

        Parameters
        ----------
        self : Argument
            The instance of the Argument dataclass.

        Returns
        -------
        None
            This method does not return any value. Validation occurs in-place.

        Raises
        ------
        TypeError
            If module_name, class_name, or full_class_path are not strings.
        ValueError
            If the 'type' field is None when default is None.

        Notes
        -----
        Validation is performed only when default is None and resolved is True.
        """
        # Skip validation if a default value is provided
        if self.default is None and self.resolved:
            # Validate module_name is a string
            if not isinstance(self.module_name, str):
                error_msg = (
                    f"module_name must be str, got {type(self.module_name).__name__}"
                )
                raise TypeError(error_msg)
            # Validate class_name is a string
            if not isinstance(self.class_name, str):
                error_msg = (
                    f"class_name must be str, got {type(self.class_name).__name__}"
                )
                raise TypeError(error_msg)
            # Ensure type field is not None for required arguments
            if self.type is None:
                error_msg = (
                    "The 'type' field must not be None. Provide a valid Python type "
                    "object for the dependency."
                )
                raise ValueError(error_msg)
            # Validate full_class_path is a string
            if not isinstance(self.full_class_path, str):
                error_msg = (
                    "full_class_path must be str, "
                    f"got {type(self.full_class_path).__name__}"
                )
                raise TypeError(error_msg)
