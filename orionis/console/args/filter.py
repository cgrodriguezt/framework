from __future__ import annotations
from typing import Any, ClassVar, TYPE_CHECKING
from orionis.console.enums.actions import ArgumentAction
from orionis.support.patterns.final.meta import Final

if TYPE_CHECKING:
    from orionis.console.args.argument import CLIArgument

class CLIArgumentFilter(metaclass=Final):

    CONST_ACTIONS: ClassVar[list] = [
        ArgumentAction.STORE_CONST.value,
        ArgumentAction.APPEND_CONST.value,
    ]

    TYPE_IGNORED_ACTIONS: ClassVar[list] = [
        ArgumentAction.STORE_TRUE.value,
        ArgumentAction.STORE_FALSE.value,
        ArgumentAction.STORE_CONST.value,
        ArgumentAction.APPEND_CONST.value,
        ArgumentAction.COUNT.value,
        ArgumentAction.HELP.value,
        ArgumentAction.VERSION.value,
    ]

    METAVAR_IGNORED_ACTIONS: ClassVar[list] = [
        ArgumentAction.STORE_TRUE.value,
        ArgumentAction.STORE_FALSE.value,
        ArgumentAction.COUNT.value,
        ArgumentAction.HELP.value,
        ArgumentAction.VERSION.value,
    ]

    DEFAULT_IGNORED_ACTIONS: ClassVar[list] = [
        ArgumentAction.STORE_TRUE.value,
        ArgumentAction.STORE_FALSE.value,
        ArgumentAction.STORE_CONST.value,
        ArgumentAction.APPEND_CONST.value,
        ArgumentAction.HELP.value,
        ArgumentAction.VERSION.value,
    ]

    REQUIRED_IGNORED_ACTIONS: ClassVar[list] = [
        ArgumentAction.HELP.value,
        ArgumentAction.VERSION.value,
    ]

    def __init__(self, argument: CLIArgument) -> None:
        """
        Initialize CLIArgumentBuilder with a CLIArgument instance.

        Parameters
        ----------
        argument : CLIArgument
            The CLIArgument instance to be used for building.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Validate that argument is not None
        if argument is None:
            error_msg = "CLIArgument cannot be None for filtering"
            raise ValueError(error_msg)

        # Store the argument instance for further processing
        self.__argument = argument

        # Determine if the argument is positional or optional
        self.__verifyIsPositionalOrOptional()

        # Set default keyword arguments for the argument
        self.__defaultKwargs()

    def __verifyIsPositionalOrOptional(self) -> None:
        """
        Determine if the argument is positional or optional.

        Checks if any flag in the argument starts with a dash to identify
        optional arguments. Sets internal flags accordingly.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Validate that flags exist and are not empty
        flags = getattr(self.__argument, "flags", None)
        if not flags:
            error_msg = "Argument must have `flags` (list or str) at filter stage."
            raise ValueError(error_msg)

        # Convert single string flag to list for consistent processing
        if isinstance(flags, str):
            flags = [flags]

        # Check if any flag starts with '-' to identify optional arguments
        self.__is_optional = any(
            isinstance(f, str) and f.startswith("-")
            for f in flags
        )

        # Set positional flag based on optional status
        self.__is_positional = not self.__is_optional

    def __defaultKwargs(self) -> None:
        """
        Set default keyword arguments for the CLI argument.

        Initializes the internal dictionary of keyword arguments using the
        properties of the CLIArgument instance. These arguments are used
        for configuring the CLI argument.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Create a dictionary with default keyword arguments from the argument
        self.__kwargs = {
            "help": self.__argument.help,
            "default": self.__argument.default,
            "required": self.__argument.required and self.__is_optional,
            "metavar": self.__argument.metavar,
            "dest": self.__argument.dest,
            "choices": self.__argument.choices,
            "action": self.__argument.action,
            "nargs": self.__argument.nargs,
            "type": self.__argument.type,
        }

    def __defineConstForActions(self) -> None:
        """
        Define the 'const' parameter for specific argument actions.

        Add the 'const' parameter to the keyword arguments if the argument's
        action requires it or if nargs is '?' and const is not None.

        Returns
        -------
        None
            Always returns None. No value is returned.
        """
        # Check if the action requires a constant value or if nargs is '?'
        # and const is provided, then add 'const' to kwargs.
        if (self.__argument.action in self.CONST_ACTIONS or
            (self.__argument.nargs == "?" and self.__argument.const is not None)):
            self.__kwargs["const"] = self.__argument.const

    def __defineVersion(self) -> None:
        """
        Set the version parameter for the version action.

        If the argument's action is 'version', assign the 'version' attribute
        in the kwargs dictionary. The value is taken from the instance's
        'version' attribute if present, otherwise defaults to '1.0.0'.

        Returns
        -------
        None
            Always returns None. No value is returned.
        """
        # Check if the action is 'version' and set the version parameter
        if self.__argument.action == ArgumentAction.VERSION.value:
            self.__kwargs["version"] = getattr(self.__argument, "version", "1.0.0")

    def __filterKwargs(self) -> dict[str, Any]: # NOSONAR
        """
        Filter keyword arguments by removing None values and incompatible parameters.

        Filters out None values and skips parameters that are not compatible with
        the argument's action or type. Ensures only valid keyword arguments are
        included for further processing.

        Returns
        -------
        dict of str to Any
            Dictionary containing filtered keyword arguments.
        """
        filtered_kwargs = {}

        # Iterate over all keyword arguments to filter them
        for k, v in self.__kwargs.items():

            # Skip empty or None metavar
            if k == "metavar" and v is None:
                continue

            # Include only non-None values
            if v is not None:

                # Skip type for actions that ignore type
                if (
                    k == "type"
                    and self.__argument.action in self.TYPE_IGNORED_ACTIONS
                ):
                    continue

                # Skip metavar for actions that ignore metavar
                if (
                    k == "metavar"
                    and self.__argument.action in self.METAVAR_IGNORED_ACTIONS
                ):
                    continue

                # Skip default for actions that ignore default
                if (
                    k == "default"
                    and self.__argument.action in self.DEFAULT_IGNORED_ACTIONS
                ):
                    continue

                # Skip required for actions that ignore required
                if (
                    k == "required"
                    and self.__argument.action in self.REQUIRED_IGNORED_ACTIONS
                ):
                    continue

                # Skip empty metavar for positional arguments
                if k == "metavar" and self.__is_positional and v == "":
                    continue

                # Add the valid keyword argument to the filtered dictionary
                filtered_kwargs[k] = v

        # Return the filtered keyword arguments
        return filtered_kwargs


    def argparseKwargs(self) -> dict[str, Any]:
        """
        Build and return keyword arguments for argparse compatibility.

        Constructs a dictionary mapping CLIArgument attributes to argparse
        parameters. Filters out None values and excludes parameters that are
        incompatible with the argument type or action.

        Returns
        -------
        dict of str to Any
            Filtered dictionary of keyword arguments for
            argparse.ArgumentParser.add_argument().
        """
        # Add 'const' parameter if required by the argument's action
        self.__defineConstForActions()

        # Add 'version' parameter if the action is 'version'
        self.__defineVersion()

        # Filter out None values and incompatible parameters
        filtered_kwargs = self.__filterKwargs()

        # Remove parameters incompatible with positional arguments
        if self.__is_positional:

            # Remove "required" for positional arguments
            filtered_kwargs.pop("required", None)

            # Remove "dest" for positional arguments
            # (argparse determines this automatically)
            filtered_kwargs.pop("dest", None)

            # Remove redundant metavar if it matches flag name
            if (
                "metavar" in filtered_kwargs
                and self.__argument.flags
                and len(self.__argument.flags) == 1
            ):
                flag_upper = self.__argument.flags[0].upper()
                if filtered_kwargs["metavar"] == flag_upper:
                    del filtered_kwargs["metavar"]

        # Ensure default is integer for count action
        if (
            self.__argument.action == ArgumentAction.COUNT.value
            and "default" in filtered_kwargs
        ):
            default_val = filtered_kwargs["default"]
            if not isinstance(default_val, int):
                # Try to convert to int if possible
                try:
                    filtered_kwargs["default"] = int(default_val)
                except (ValueError, TypeError):
                    # If conversion fails, use 0 as safe default
                    filtered_kwargs["default"] = 0

        # Return filtered keyword arguments for argparse
        return filtered_kwargs
