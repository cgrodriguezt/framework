from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from orionis.console.enums.actions import ArgumentAction
from orionis.console.exceptions import CLIOrionisValueError
from orionis.console.exceptions.cli_exceptions import (
    CLIOrionisException,
    CLIOrionisRuntimeError,
    CLIOrionisTypeError,
)

if TYPE_CHECKING:
    import argparse

@dataclass(kw_only=True, frozen=True, slots=True)
class CLIArgument:
    """
    Representation of a command-line argument for argparse.

    Encapsulates properties and validation logic for creating a command-line argument
    compatible with argparse. Provides validation, type checking, and default values.

    Attributes
    ----------
    flags : List[str]
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

    Raises
    ------
    CLIOrionisValueError
        If validation fails during initialization.
    """

    flags: list[str]

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

    # ruff: noqa: PLR0912, PLR0915
    def __post_init__(self) -> None: # NOSONAR
        """
        Validate and normalize all argument attributes after initialization.

        This method performs comprehensive validation of all argument attributes
        and applies smart defaults where appropriate. It ensures the argument
        configuration is valid for use with argparse.

        Raises
        ------
        CLIOrionisValueError
            If any validation fails or invalid values are provided.
        CLIOrionisTypeError
            If a type mismatch or invalid type is detected.
        """
        # Validate flags - must be provided and non-empty
        if not self.flags:
            error_msg = "Flags list cannot be empty"
            raise CLIOrionisValueError(error_msg)

        # Convert single string flag to list for consistency
        if isinstance(self.flags, str):
            object.__setattr__(self, "flags", [self.flags])

        # Ensure flags is a list
        if not isinstance(self.flags, list):
            error_msg = "Flags must be provided as a list of strings"
            raise CLIOrionisTypeError(error_msg)

        # Validate each flag format and ensure they're strings
        for flag in self.flags:
            if not isinstance(flag, str):
                error_msg = f"Flag '{flag}' is not a string"
                raise CLIOrionisTypeError(error_msg)

        # Check for duplicate flags
        if len(set(self.flags)) != len(self.flags):
            error_msg = "Duplicate flags are not allowed in the flags list"
            raise CLIOrionisValueError(error_msg)

        # Determine primary flag (longest one, or first if only one)
        if len(self.flags) > 1:
            primary_flag = max(self.flags, key=len)
        else:
            primary_flag = self.flags[0]

        # Validate type is actually a type
        if not isinstance(self.type, type):
            error_msg = "Type must be a valid Python type or custom type class"
            raise CLIOrionisTypeError(error_msg)

        # Auto-generate help if not provided
        if self.help is None:
            clean_flag = primary_flag.lstrip("-").replace("-", " ").title()
            object.__setattr__(self, "help", f"{clean_flag} argument")

        # Ensure help is a string
        if not isinstance(self.help, str):
            error_msg = "Help text must be a string"
            raise CLIOrionisTypeError(error_msg)

        # Validate choices if provided
        if self.choices is not None:
            # Ensure choices is a list
            if not isinstance(self.choices, list):
                error_msg = "Choices must be provided as a list"
                raise CLIOrionisTypeError(error_msg)

            # Ensure all choices match the specified type
            if (
                self.type
                and not all(
                    isinstance(choice, self.type)
                    for choice in self.choices
                )
            ):
                error_msg = f"All choices must be of type {self.type.__name__}"
                raise CLIOrionisTypeError(error_msg)

        # Validate required is boolean
        if not isinstance(self.required, bool):
            error_msg = "Required field must be a boolean value (True or False)"
            raise CLIOrionisTypeError(error_msg)

        # Auto-generate metavar if not provided
        if self.metavar is None:
            metavar = primary_flag.lstrip("-").upper().replace("-", "_")
            object.__setattr__(self, "metavar", metavar)

        # Ensure metavar is a string
        if not isinstance(self.metavar, str):
            error_msg = "Metavar must be a string"
            raise CLIOrionisTypeError(error_msg)

        # Auto-generate dest if not provided
        if self.dest is None:
            dest = primary_flag.lstrip("-").replace("-", "_")
            object.__setattr__(self, "dest", dest)

        # Ensure dest is a string
        if not isinstance(self.dest, str):
            error_msg = "Destination (dest) must be a string"
            raise CLIOrionisTypeError(error_msg)

        # Ensure dest is a valid Python identifier
        if not self.dest.isidentifier():
            error_msg = f"Destination '{self.dest}' is not a valid Python identifier"
            raise CLIOrionisValueError(error_msg)

        # Normalize action value
        if isinstance(self.action, str):
            try:
                action_enum = ArgumentAction(self.action)
                object.__setattr__(self, "action", action_enum.value)
            except ValueError:
                error_msg = (
                    f"Invalid action '{self.action}'. "
                    "Please use a valid ArgumentAction value"
                )
                raise CLIOrionisValueError(error_msg) from None
        elif isinstance(self.action, ArgumentAction):
            object.__setattr__(self, "action", self.action.value)
        else:
            error_msg = "Action must be a string or an ArgumentAction enum value"
            raise CLIOrionisTypeError(error_msg)

        # Determine if this is an optional argument (starts with dash)
        is_optional = any(flag.startswith("-") for flag in self.flags)

        # Special handling for boolean types
        if self.type is bool:
            # Auto-configure action based on default value and whether it's optional
            if is_optional:
                action = (
                    ArgumentAction.STORE_FALSE.value
                    if self.default else ArgumentAction.STORE_TRUE.value
                )
                object.__setattr__(self, "action", action)
                # argparse ignores type with store_true/false actions
                object.__setattr__(self, "type", None)
            else:
                # For positional boolean arguments, keep type as bool
                pass

        # Special handling for list types
        elif self.type is list:
            if self.nargs is None:
                # Auto-configure for accepting multiple values
                object.__setattr__(self, "nargs", "+" if is_optional else "*")
            # Keep type as list for proper conversion
            # argparse expects element type, not list
            object.__setattr__(self, "type", str)

        # Handle count action - typically used for verbosity flags
        elif self.action == ArgumentAction.COUNT.value:
            object.__setattr__(self, "type", None)  # count action doesn't use type
            if self.default is None:
                object.__setattr__(self, "default", 0)

        # Handle const actions
        if self.action in (
            ArgumentAction.STORE_CONST.value,
            ArgumentAction.APPEND_CONST.value,
        ):
            if self.const is None:
                # Auto-set const based on type or use True as default
                if self.type is bool:
                    object.__setattr__(self, "const", True)
                elif self.type is int:
                    object.__setattr__(self, "const", 1)
                elif self.type is str:
                    object.__setattr__(self, "const", self.dest)
                else:
                    object.__setattr__(self, "const", True)
            object.__setattr__(self, "type", None)  # const actions don't use type

        # Handle nargs '?' - optional single argument
        elif self.nargs == "?" and self.const is None and is_optional:
            # For optional arguments with nargs='?', set a reasonable const
            object.__setattr__(self, "const", True if self.type is bool else self.dest)

        # Validate nargs compatibility
        if self.nargs is not None:
            valid_nargs = ["?", "*", "+"] + [str(i) for i in range(10)]
            if isinstance(self.nargs, int):
                if self.nargs < 0:
                    error_msg = "nargs cannot be negative"
                    raise CLIOrionisValueError(error_msg)
            elif self.nargs not in valid_nargs:
                error_msg = f"Invalid nargs value: {self.nargs}"
                raise CLIOrionisValueError(error_msg)

        # Handle version action
        if self.action == ArgumentAction.VERSION.value:
            object.__setattr__(self, "type", None)
            if "version" not in self.dest:
                object.__setattr__(self, "dest", "version")

        # Handle help action
        if self.action == ArgumentAction.HELP.value:
            object.__setattr__(self, "type", None)

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
        kwargs = self._buildParserKwargs()

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

    # ruff: noqa: C901
    def _buildParserKwargs(self) -> dict[str, Any]: # NOSONAR
        """
        Build a dictionary of keyword arguments for argparse compatibility.

        Builds a mapping of CLIArgument attributes to argparse parameters.
        Filters out None values and excludes parameters incompatible with
        the argument type or action.

        Returns
        -------
        dict of str to Any
            Dictionary of keyword arguments for argparse.ArgumentParser.add_argument().
        """
        # Determine if argument is optional (starts with dash)
        is_optional = any(flag.startswith("-") for flag in self.flags)
        is_positional = not is_optional

        # Prepare base keyword arguments for argparse
        kwargs = {
            "help": self.help,
            "default": self.default,
            "required": self.required and is_optional,
            "metavar": self.metavar,
            "dest": self.dest,
            "choices": self.choices,
            "action": self.action,
            "nargs": self.nargs,
            "type": self.type,
        }

        # Add const parameter for actions that require it
        const_actions = [
            ArgumentAction.STORE_CONST.value,
            ArgumentAction.APPEND_CONST.value,
        ]

        if (self.action in const_actions or
            (self.nargs == "?" and self.const is not None)):
            kwargs["const"] = self.const

        # Add version parameter for version action
        if self.action == ArgumentAction.VERSION.value and hasattr(self, "version"):
            kwargs["version"] = getattr(self, "version", None)

        # Actions that ignore certain parameters
        type_ignored_actions = [
            ArgumentAction.STORE_TRUE.value,
            ArgumentAction.STORE_FALSE.value,
            ArgumentAction.STORE_CONST.value,
            ArgumentAction.APPEND_CONST.value,
            ArgumentAction.COUNT.value,
            ArgumentAction.HELP.value,
            ArgumentAction.VERSION.value,
        ]
        metavar_ignored_actions = [
            ArgumentAction.STORE_TRUE.value,
            ArgumentAction.STORE_FALSE.value,
            ArgumentAction.COUNT.value,
            ArgumentAction.HELP.value,
            ArgumentAction.VERSION.value,
        ]
        default_ignored_actions = [
            ArgumentAction.STORE_TRUE.value,
            ArgumentAction.STORE_FALSE.value,
            ArgumentAction.STORE_CONST.value,
            ArgumentAction.APPEND_CONST.value,
            ArgumentAction.HELP.value,
            ArgumentAction.VERSION.value,
        ]

        # Filter out None values and incompatible parameters
        filtered_kwargs = {}
        for k, v in kwargs.items():
            if v is not None:

                # Skip type for actions that ignore it
                if k == "type" and self.action in type_ignored_actions:
                    continue

                # Skip metavar for actions that ignore it
                if k == "metavar" and self.action in metavar_ignored_actions:
                    continue

                # Skip default for actions that ignore it
                if k == "default" and self.action in default_ignored_actions:
                    continue

                # Skip empty metavar for positional arguments
                if k == "metavar" and is_positional and v == "":
                    continue

                filtered_kwargs[k] = v

        # Remove parameters incompatible with positional arguments
        if is_positional:

            # Remove "required" for positional arguments
            filtered_kwargs.pop("required", None)

            # Remove "dest" for positional arguments
            filtered_kwargs.pop("dest", None)

            # Remove redundant metavar if it matches flag name
            if "metavar" in filtered_kwargs and len(self.flags) == 1:
                flag_upper = self.flags[0].upper()
                if filtered_kwargs["metavar"] == flag_upper:
                    del filtered_kwargs["metavar"]

        # Ensure default is integer for count action
        if (self.action == ArgumentAction.COUNT.value and
            "default" in filtered_kwargs and
            not isinstance(filtered_kwargs["default"], int)):
            filtered_kwargs["default"] = 0

        # Return filtered keyword arguments for argparse
        return filtered_kwargs
