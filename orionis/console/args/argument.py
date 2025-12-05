from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from orionis.console.args.constructor import CLIArgumentConstructor
from orionis.console.args.filter import CLIArgumentFilter
from orionis.console.enums.actions import ArgumentAction
from orionis.console.exceptions import CLIOrionisValueError
from orionis.console.exceptions.cli_exceptions import (
    CLIOrionisException,
    CLIOrionisRuntimeError,
    CLIOrionisTypeError,
)
from orionis.support.entities.base import BaseEntity

if TYPE_CHECKING:
    import argparse

@dataclass(kw_only=True, frozen=True, slots=True)
class CLIArgument(BaseEntity):
    """
    Representation of a command-line argument for argparse.

    Encapsulates properties and validation logic for creating a command-line argument
    compatible with argparse. Provides validation, type checking, and default values.

    Attributes
    ----------
    name : str, optional
        Name of the argument (for positional arguments).
    flags : list[str] | str, optional
        List of argument flags (e.g., ['--export', '-e']).
    type : Type
        Data type for the argument.
    help : str, optional
        Argument description. Auto-generated if not provided.
    default : Any, optional
        Default value for the argument.
    choices : List[Any], optional
        Valid values for the argument.
    required : bool, default False
        Indicates if the argument is required.
    metavar : str, optional
        Name for display in help messages.
    dest : str, optional
        Destination name in the namespace.
    action : Union[str, ArgumentAction], default ArgumentAction.STORE
        Action to perform when the argument is encountered.
    nargs : Union[int, str], optional
        Number of arguments expected.
    const : Any, optional
        Constant value for store_const or append_const actions.
    """

    name: str | None = field(
        default=None,
        metadata={
            "description": "Name of the argument (for positional arguments).",
            "default": None,
        },
    )

    flags: list[str] | str | None = field(
        default=None,
        metadata={
            "description": "List of argument flags (e.g., ['--export', '-e']).",
            "default": None,
        },
    )

    type: type

    help: str | None = None

    default: Any = field(
        default=None,
        metadata={
            "description": "Default value for the argument.",
            "default": None,
        },
    )

    choices: list | None = field(
        default=None,
        metadata={
            "description": "List of valid choices for the argument.",
            "default": None,
        },
    )

    required: bool = field(
        default=False,
        metadata={
            "description": "Indicates if the argument is required.",
            "default": False,
        },
    )

    metavar: str | None = field(
        default=None,
        metadata={
            "description": "Metavar for displaying in help messages.",
            "default": None,
        },
    )

    dest: str | None = field(
        default=None,
        metadata={
            "description": "Destination name for the argument in the namespace.",
            "default": None,
        },
    )

    action: str | ArgumentAction | None = field(
        default=ArgumentAction.STORE,
        metadata={
            "description": "Action to perform with the argument.",
            "default": ArgumentAction.STORE.value,
        },
    )

    nargs: int | str | None = field(
        default=None,
        metadata={
            "description": "Number of arguments expected (e.g., 1, 2, '+', '*').",
            "default": None,
        },
    )

    const: Any = field(
        default=None,
        metadata={
            "description": "Constant value for store_const or append_const actions.",
            "default": None,
        },
    )

    def __post_init__(self) -> None:
        """
        Initialize CLIArgument fields after object creation.

        Use CLIArgumentConstructor to build and validate argument properties.
        Assign constructed values to the instance using object.__setattr__.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Build argument dictionary using CLIArgumentConstructor
        constructor = CLIArgumentConstructor(self)

        # Construct final argument values
        constructed_fields = constructor.construct()

        # Assign constructed values to instance fields
        for field_name, field_value in constructed_fields.items():
            object.__setattr__(self, field_name, field_value)

    def addToParser(self, parser: argparse.ArgumentParser) -> None:
        """
        Add this CLIArgument to an argparse.ArgumentParser.

        Build keyword arguments for argparse and register the argument with all flags.
        Handle conversion and validation for compatibility.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Parser to which the argument will be added.

        Returns
        -------
        None
            This method modifies the parser in place and does not return a value.

        Raises
        ------
        CLIOrionisValueError
            If argument addition fails due to invalid configuration or conflicts.
        CLIOrionisTypeError
            If there is a type mismatch in argument configuration.
        CLIOrionisRuntimeError
            If a runtime error occurs during argument addition.
        CLIOrionisException
            If an unexpected error occurs.
        """
        # Build keyword arguments for argparse from CLIArgument attributes
        kwargs = CLIArgumentFilter(self).argparseKwargs()

        # Try to add the argument to the parser, handling possible errors
        try:
            parser.add_argument(*self.flags, **kwargs)

        # Handle type errors during argument addition
        except TypeError as e:
            error_msg = (
                f"Type error adding argument {self.flags}: {e}"
            )
            raise CLIOrionisTypeError(error_msg) from e

        # Handle value errors during argument addition
        except ValueError as e:
            error_msg = (
                f"Value error adding argument {self.flags}: {e}"
            )
            raise CLIOrionisValueError(error_msg) from e

        # Handle runtime errors during argument addition
        except RuntimeError as e:
            error_msg = (
                f"Runtime error adding argument {self.flags}: {e}"
            )
            raise CLIOrionisRuntimeError(error_msg) from e

        # Handle any other unexpected errors
        except Exception as e:
            error_msg = (
                f"Unexpected error adding argument {self.flags}: {e}"
            )
            raise CLIOrionisException(error_msg) from e
