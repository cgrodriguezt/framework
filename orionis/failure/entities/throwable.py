from __future__ import annotations
from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class Throwable:
    """
    Represent a throwable entity within the framework.

    Parameters
    ----------
    classtype : type
        The class type of the throwable, typically an exception class.
    message : str
        The error message describing the throwable.
    args : tuple
        Arguments passed to the throwable, usually corresponding to the
        exception arguments.
    traceback : str | None, optional
        The traceback information as a string, if available. Defaults to None.

    Returns
    -------
    Throwable
        An instance encapsulating exception details.
    """

    # The type of the throwable (e.g., Exception class)
    classtype: type

    # The error message associated with the throwable
    message: str

    # Arguments passed to the throwable
    args: tuple

    # Optional traceback information as a string
    traceback: str | None = None
