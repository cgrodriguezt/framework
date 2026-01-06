from __future__ import annotations
import re
from typing import Any, ClassVar, TYPE_CHECKING
from orionis.console.args.types import ALLOWED_TYPES
from orionis.console.enums.actions import ArgumentAction
from orionis.support.patterns.final.meta import Final

if TYPE_CHECKING:
    from orionis.console.args.argument import CLIArgument

class CLIArgumentConstructor(metaclass=Final):

    # ruff: noqa: C901, PLR2004, PLR0912

    ACTIONS_IGNORING_METAVAR: ClassVar[set[str]] = {
        ArgumentAction.STORE_TRUE.value,
        ArgumentAction.STORE_FALSE.value,
        ArgumentAction.COUNT.value,
        ArgumentAction.HELP.value,
        ArgumentAction.VERSION.value,
    }

    def __init__(self, argument: CLIArgument) -> None:
        """
        Initialize the CLIArgumentConstructor with a CLIArgument instance.

        Parameters
        ----------
        argument : CLIArgument
            The CLIArgument instance to be processed.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Validate that argument is not None
        if argument is None:
            error_msg = "CLIArgument cannot be None"
            raise ValueError(error_msg)

        # Store the argument as a dictionary for further processing
        argument_dict = argument.toDict()

        # Validate that toDict() returned a valid dictionary
        if not isinstance(argument_dict, dict) or not argument_dict:
            error_msg = "Invalid CLIArgument: toDict() returned empty or invalid data"
            raise ValueError(error_msg)

        # Store the argument dictionary
        self.__argument = argument_dict

        # Track if the argument is positional
        self.__is_positional_argument: bool = False

        # Store the original type of the argument
        self.__original_type: type | None = None

        # Track if the argument is optional
        self.__is_optional: bool = False

        # Store the primary flag for the argument
        self.__primary_flag: str | None = None

    def construct(self) -> dict[str, Any]:
        """
        Construct and return a processed dictionary representing the argument.

        Validates and processes the argument properties, then returns the
        resulting dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary containing the argument's flags and properties.
        """
        # Validate that either name or flags are provided
        self.__validateNameOrFlags()

        # Validate and assign positional name if applicable
        self.__validateAndAssignPositionalName()

        # Validate and assign flags for the argument
        self.__validateAndAssignFlags()

        # Validate and assign the action attribute
        self.__validateAndAssignAction()

        # Validate and assign the type of the argument
        self.__validateAndAssignType()

        # Determine if the argument is optional
        self.__determineIfOptional()

        # Handle optional boolean and list arguments
        self.__handleOptionalBoolean()

        # Handle special argument actions
        self.__handleSpecialActions()

        # Assign the primary flag for the argument
        self.__assignPrimaryFlag()

        # Generate and assign 'metavar' and 'dest' properties
        self.__assignMetavarAndDest()

        # Validate and assign the 'choices' attribute
        self.__validateAndAssignChoices()

        # Validate that the 'required' field is a boolean value
        self.__validateRequiredType()

        # Assign default help text if not provided
        self.__assignDefaultHelp()

        # Validate and assign the 'nargs' attribute
        self.__validateAndAssignNargs()

        # Return the processed argument dictionary
        return self.__argument

    def __validateNameOrFlags(self) -> None:
        """
        Validate that either name or flags are provided.

        Raises
        ------
        ValueError
            If neither name nor flags are provided.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Ensure that at least one of name or flags is present
        if not self.__argument.get("name") and not self.__argument.get("flags"):
            error_msg = "Either name or flags must be provided"
            raise ValueError(error_msg)

    def __validateAndAssignPositionalName(self) -> None:
        """
        Validate and assign the argument name as positional if appropriate.

        Raises
        ------
        TypeError
            If the name is not a string.
        ValueError
            If the name starts with '-' or contains invalid characters, or if
            both name and flags are provided.

        Returns
        -------
        None
            Always returns None.
        """
        # Validate that the name is provided and is a string
        if self.__argument.get("name") is not None:

            # Ensure the name is a string
            if not isinstance(self.__argument.get("name"), str):

                # Name must be a string
                error_msg = "Name must be a string"
                raise TypeError(error_msg)

            # Ensure the name does not start with '-'
            if str(self.__argument.get("name")).startswith("-"):

                # Name cannot start with '-'
                error_msg = "Name cannot start with '-'"
                raise ValueError(error_msg)

            # Ensure the name contains only valid characters
            if not re.match(
                r"^[A-Za-z0-9][A-Za-z0-9_\-\.]*$",
                self.__argument.get("name"),
            ):

                # Name contains invalid characters
                invalid_name = self.__argument.get("name")
                error_msg = (
                    f"Name '{invalid_name}' contains invalid characters. "
                    "Use only letters, numbers, underscore, hyphen, and dot."
                )
                raise ValueError(error_msg)

            # Ensure name and flags are not used together
            if self.__argument.get("flags"):

                # Name cannot be used together with flags
                error_msg = "Name cannot be used together with flags"
                raise ValueError(error_msg)

            # If flags are not provided, treat name as positional argument
            if not self.__argument.get("flags"):

                # Mark as positional argument and assign flags
                self.__is_positional_argument = True
                self.__argument["flags"] = [self.__argument.get("name")]

    def __validateAndAssignFlags(self) -> None: # NOSONAR
        """
        Validate and assign flags for the argument.

        Ensures that flags are present, are of the correct type, and follow the
        required format for positional and optional arguments.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Ensure flags are provided and not empty
        if not self.__argument.get("flags"):
            error_msg = "Flags list cannot be empty"
            raise ValueError(error_msg)

        # Convert a single string flag to a list for consistency
        if isinstance(self.__argument.get("flags"), str):
            single_flag: str = self.__argument.get("flags")
            self.__argument["flags"] = [single_flag]

            # Check if the flag is incorrectly specified for positional arguments
            if (
                not single_flag.startswith("-")
                and not self.__is_positional_argument
            ):
                error_msg = (
                    f"Flag '{single_flag}' does not start with '-'. "
                    f"For positional arguments, use 'name=\"{single_flag}\"' "
                    f"instead of 'flags=\"{single_flag}\"'"
                )
                raise ValueError(error_msg)

        # Ensure flags is a list
        if not isinstance(self.__argument.get("flags"), list):
            error_msg = "Flags must be provided as a list of strings"
            raise TypeError(error_msg)

        # Validate each flag's format and type
        for flag in self.__argument.get("flags"):
            if not isinstance(flag, str):
                arg_context = (
                    self.__argument.get("flags") or self.__argument.get("name")
                )
                error_msg = (
                    f"Flag '{flag}' is not a string (argument: {arg_context})"
                )
                raise TypeError(error_msg)

            # For optional arguments, flags must start with '-' and follow format rules
            if not self.__is_positional_argument and not flag.startswith("-"):
                if len(self.__argument.get("flags")) == 1:
                    error_msg = (
                        f"Flag '{flag}' does not start with '-'. "
                        f"For positional arguments, use 'name=\"{flag}\"' "
                        f"instead of 'flags=[\"{flag}\"]'"
                    )
                else:
                    arg_context = self.__argument.get("flags")
                    error_msg = (
                        f"Each flag must start with '-', but got '{flag}' "
                        f"(argument: {arg_context})"
                    )
                raise ValueError(error_msg)

            # Validate flag format for optional arguments
            if not self.__is_positional_argument:
                if flag.startswith("--") and len(flag) < 3:
                    arg_context = self.__argument.get("flags")
                    error_msg = (
                        f"Invalid long flag '{flag}' - must be at least '--x' "
                        f"(argument: {arg_context})"
                    )
                    raise ValueError(error_msg)
                if (
                    flag.startswith("-")
                    and not flag.startswith("--")
                    and len(flag) != 2
                ):
                    arg_context = self.__argument.get("flags")
                    error_msg = (
                        f"Invalid short flag '{flag}' - must be exactly '-x' "
                        f"format (argument: {arg_context})"
                    )
                    raise ValueError(error_msg)

        # Check for duplicate flags
        if len(set(self.__argument.get("flags"))) != len(
            self.__argument.get("flags"),
        ):
            error_msg = "Duplicate flags are not allowed in the flags list"
            raise ValueError(error_msg)

    def __validateAndAssignAction(self) -> None:
        """
        Validate and assign the action attribute for the argument.

        Converts the action to an ArgumentAction enum value if it is a string.
        Ensures the action is either a string or an ArgumentAction enum value.

        Returns
        -------
        None
            Always returns None.
        """
        # Extract action for validation.
        action = self.__argument.get("action")

        # Convert string action to ArgumentAction enum if necessary
        if isinstance(action, str):

            # Try to convert string to ArgumentAction enum and get its value
            try:
                enum_action = ArgumentAction(action)
                self.__argument["action"] = enum_action.value
            except ValueError:
                error_msg = (
                    f"Invalid action '{action}'. "
                    "Please use a valid ArgumentAction value"
                )
                raise ValueError(error_msg) from None

        # If action is already an ArgumentAction enum, assign its value
        elif isinstance(action, ArgumentAction):
            self.__argument["action"] = action.value

        # Raise error if action is neither string nor ArgumentAction enum
        else:
            error_msg = (
                "Action must be a string or an ArgumentAction enum value"
            )
            raise TypeError(error_msg)

    def __validateAndAssignType(self) -> None:
        """
        Validate and assign the argument type.

        Parameters
        ----------
        self : CLIArgumentConstructor
            The instance of CLIArgumentConstructor.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        TypeError
            If the argument type is not among the allowed types.
        """
        # Extract the argument type from the argument dictionary
        arg_type: type[Any] | None = self.__argument.get("type")

        # Check if the argument type is allowed
        if arg_type not in ALLOWED_TYPES:
            error_msg = (
                "The type used for the argument is not valid. Allowed types are: "
                f"{ALLOWED_TYPES}"
            )
            raise TypeError(error_msg)

        # Assign the validated type back to the argument dictionary
        self.__original_type = arg_type

    def __determineIfOptional(self) -> None:
        """
        Determine if the argument is optional.

        An argument is considered optional if any flag starts with '-'.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Set __is_optional to True if any flag starts with '-'
        self.__is_optional = any(
            flag.startswith("-") for flag in self.__argument.get("flags")
        )

    def __handleOptionalBoolean(self) -> None: # NOSONAR
        """
        Handle optional boolean and list arguments.

        For optional boolean arguments, set the action to STORE_FALSE or
        STORE_TRUE based on the default value, and set the type to None.
        For list arguments, set nargs and type accordingly. For count action,
        set type and default.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Handle optional boolean arguments
        if self.__original_type is bool:

            # Only optional arguments (flags) can be boolean
            if self.__is_optional:

                # Boolean arguments cannot use 'nargs'
                if self.__argument.get("nargs") is not None:
                    arg_context = (
                        self.__argument.get("flags") or self.__argument.get("name")
                    )
                    error_msg = (
                        "Boolean arguments cannot use 'nargs'"
                        f" (argument: {arg_context})"
                    )
                    raise ValueError(error_msg)

                # Normalize default to explicit boolean
                default = self.__argument.get("default")
                if default is None:
                    default = False
                    self.__argument["default"] = False

                # Set action based on explicit boolean value
                if default is True:
                    self.__argument["action"] = ArgumentAction.STORE_FALSE.value
                else:
                    self.__argument["action"] = ArgumentAction.STORE_TRUE.value

                # Set type to None for optional boolean arguments
                self.__argument["type"] = None

        # Handle list arguments
        elif self.__original_type is list:

            # Set nargs for list arguments if not specified
            if self.__argument.get("nargs") is None:

                # Use '*' for optional, '+' for positional arguments
                self.__argument["nargs"] = "*" if self.__is_optional else "+"

            # Set type to str for list arguments
            self.__argument["type"] = str

        # Handle count action
        elif self.__argument.get("action") == ArgumentAction.COUNT.value:

            # COUNT action cannot use 'nargs'
            if self.__argument.get("nargs") is not None:
                arg_context = (
                    self.__argument.get("flags") or self.__argument.get("name")
                )
                error_msg = (
                    f"COUNT action cannot use 'nargs' (argument: {arg_context})"
                )
                raise ValueError(error_msg)

            # Set type to None for count action
            self.__argument["type"] = None

            # Set default to 0 if not specified
            if self.__argument.get("default") is None:
                self.__argument["default"] = 0

    def __handleSpecialActions(self) -> None:
        """
        Handle special argument actions and assign related properties.

        This method processes STORE_CONST, APPEND_CONST, VERSION, and HELP actions.
        It sets the 'const', 'type', and 'version' properties as required.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Extract action for processing
        action: str | None = self.__argument.get("action")

        # Handle STORE_CONST and APPEND_CONST actions
        if action in (
            ArgumentAction.STORE_CONST.value,
            ArgumentAction.APPEND_CONST.value,
        ):
            self.__handleConstActions()

        # Handle VERSION action
        if action == ArgumentAction.VERSION.value:
            self.__handleVersionAction()

        # Handle HELP action
        if action == ArgumentAction.HELP.value:
            self.__handleHelpAction()

    def __handleConstActions(self) -> None:
        """
        Handle STORE_CONST and APPEND_CONST actions for CLI arguments.

        Raises
        ------
        ValueError
            If 'const' is not provided or if 'nargs' is set with STORE_CONST.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Ensure 'const' value is provided for STORE_CONST/APPEND_CONST actions
        if self.__argument.get("const") is None:
            arg_context = self.__argument.get("flags") or self.__argument.get("name")
            error_msg = (
                f"{self.__argument.get('action').upper()} action requires a "
                f"'const' value (argument: {arg_context})"
            )
            raise ValueError(error_msg)

        # STORE_CONST cannot be used with 'nargs'
        if (
            self.__argument.get("nargs") is not None
            and self.__argument.get("action") == ArgumentAction.STORE_CONST.value
        ):
            arg_context = self.__argument.get("flags") or self.__argument.get("name")
            error_msg = (
                f"STORE_CONST action cannot use 'nargs' (argument: {arg_context})"
            )
            raise ValueError(error_msg)

        # Set type to None for const actions
        self.__argument["type"] = None

    def __handleVersionAction(self) -> None:
        """
        Handle the VERSION action for CLI arguments.

        Validates that 'nargs' is not set for VERSION action, sets the argument
        type to None, and assigns a default version if not provided.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Raise error if 'nargs' is set for VERSION action
        if self.__argument.get("nargs") is not None:
            arg_context = self.__argument.get("flags") or self.__argument.get("name")
            error_msg = (
                f"VERSION action cannot use 'nargs' (argument: {arg_context})"
            )
            raise ValueError(error_msg)

        # Set type to None for VERSION action
        self.__argument["type"] = None

        # Assign default version if not provided
        if self.__argument.get("version") is None:
            self.__argument["version"] = "1.0.0"

    def __handleHelpAction(self) -> None:
        """
        Handle the HELP action for CLI arguments.

        Validates that 'nargs' is not set for HELP action and sets the argument
        type to None.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Raise error if 'nargs' is set for HELP action
        if self.__argument.get("nargs") is not None:
            arg_context = self.__argument.get("flags") or self.__argument.get("name")
            error_msg = (
                f"HELP action cannot use 'nargs' (argument: {arg_context})"
            )
            raise ValueError(error_msg)

        # Set type to None for HELP action
        self.__argument["type"] = None

    def __assignPrimaryFlag(self) -> None:
        """
        Assign the primary flag for the argument.

        Select the longest flag as the primary flag if multiple flags exist.
        Otherwise, select the single flag present.

        Returns
        -------
        None
            This method does not return any value.
        """
        flags = self.__argument.get("flags")

        # Determine the primary flag based on the number of flags
        if len(flags) > 1:

            # Select the longest flag as the primary flag
            self.__primary_flag = max(flags, key=len)
        else:

            # Use the single flag as the primary flag
            self.__primary_flag = flags[0]

    def __assignMetavarAndDest(self) -> None:
        """
        Assign 'metavar' and 'dest' properties for the argument.

        Generates the 'metavar' property based on the argument's action, type,
        and positional status. Also generates the 'dest' property, ensuring it
        is a valid Python identifier. Adjusts for special actions such as
        VERSION.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Set 'metavar' to None if the action ignores it
        if self.__argument.get("action") in self.ACTIONS_IGNORING_METAVAR:
            self.__argument["metavar"] = None

        # Generate 'metavar' for non-boolean, non-positional arguments
        elif (
            self.__argument.get("metavar") is None
            and self.__original_type is not bool
            and not self.__is_positional_argument
        ):
            metavar = (
                self.__primary_flag.lstrip("-").upper().replace("-", "_")
            )
            self.__argument["metavar"] = metavar

        # Validate 'metavar' type
        if (
            self.__argument.get("metavar") is not None
            and not isinstance(self.__argument.get("metavar"), str)
        ):
            error_msg = "Metavar must be a string"
            raise TypeError(error_msg)

        # Generate 'dest' if not already set
        if self.__argument.get("dest") is None:
            if not self.__is_positional_argument:
                # Assign 'dest' for optional arguments
                self.__argument["dest"] = (
                    self.__primary_flag.lstrip("-")
                    .replace("-", "_")
                    .replace(".", "_")
                )
            else:
                # Assign 'dest' for positional arguments
                self.__argument["dest"] = self.__argument.get("name")

        # Adjust 'dest' for VERSION action
        if (
            self.__argument.get("action") == ArgumentAction.VERSION.value
            and "version" not in self.__argument.get("dest")
        ):
            self.__argument["dest"] = "version"

        # Validate 'dest' type
        if not isinstance(self.__argument.get("dest"), (str, type(None))):
            error_msg = "Destination (dest) must be a string"
            raise TypeError(error_msg)

        # Validate 'dest' as a Python identifier
        if (
            self.__argument.get("dest") is not None
            and not str(self.__argument.get("dest")).isidentifier()
        ):
            error_msg = (
                f"Destination '{self.__argument.get('dest')}' is not a valid "
                "Python identifier"
            )
            raise ValueError(error_msg)

    def __validateAndAssignChoices(self) -> None: # NOSONAR
        """
        Validate and assign the 'choices' attribute.

        Ensure 'choices' is a list and all elements match the original argument
        type or can be converted to it.

        Returns
        -------
        None
            This method does not return any value.
        """
        choices = self.__argument.get("choices")

        # Validate choices if provided
        if choices is not None:
            arg_context = self.__argument.get("flags") or self.__argument.get("name")

            # Ensure choices is a list
            if not isinstance(choices, list):
                error_msg = (
                    f"Choices must be provided as a list (argument: {arg_context})"
                )
                raise TypeError(error_msg)

            # Ensure original_type is set for type validation
            if self.__original_type is None:
                error_msg = (
                    f"Cannot validate choices: no type specified "
                    f"(argument: {arg_context})"
                )
                raise ValueError(error_msg)

            # Check that all choices match or can be converted to the original type
            invalid_choices = []
            for choice in choices:
                if not isinstance(choice, self.__original_type):
                    try:
                        self.__original_type(choice)
                    except (ValueError, TypeError):
                        invalid_choices.append(choice)

            if invalid_choices:
                error_msg = (
                    f"Choices {invalid_choices} cannot be converted to type "
                    f"{self.__original_type.__name__} (argument: {arg_context})"
                )
                raise TypeError(error_msg)

    def __validateRequiredType(self) -> None:
        """
        Validate that the 'required' field is a boolean.

        Ensures the 'required' field in the argument dictionary is a boolean
        value. Raises a TypeError if the value is not a boolean.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Ensure the 'required' field is a boolean value
        if not isinstance(self.__argument.get("required"), bool):
            error_msg = (
                "Required field must be a boolean value (True or False)"
            )
            raise TypeError(error_msg)

    def __assignDefaultHelp(self) -> None:
        """
        Assign default help text if not provided.

        Assign a default help message based on the primary flag if the 'help'
        attribute is missing. Validate that the help text is a string.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Assign a default help message if 'help' is not set
        if self.__argument.get("help") is None:

            # Clean the primary flag for display in the help message
            clean_flag = self.__primary_flag.lstrip("-").replace("-", " ").title()
            help_msg = f"{clean_flag} argument"
            self.__argument["help"] = help_msg

        # Validate that help text is a string
        if not isinstance(self.__argument.get("help"), str):
            error_msg = "Help text must be a string"
            raise TypeError(error_msg)

    def __validateAndAssignNargs(self) -> None: # NOSONAR
        """
        Validate and assign the 'nargs' attribute.

        Validate that 'nargs' is a non-negative integer or a valid string
        ('?', '*', '+'). Assign a default value to 'const' if 'nargs' is '?'
        and 'const' is not set. Set default to an empty list for '*' or '+'
        if not specified.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Extract 'nargs' for validation
        nargs: int | str | None = self.__argument.get("nargs")

        # Validate 'nargs' if provided
        if nargs is not None:

            # Check if 'nargs' is a non-negative integer
            if isinstance(nargs, int):
                if nargs < 0:
                    error_msg = "nargs cannot be negative"
                    raise ValueError(error_msg)

            # Check if 'nargs' is a valid string or convertible to int
            elif isinstance(nargs, str):
                if nargs not in ["?", "*", "+"]:
                    try:
                        nargs_int = int(nargs)
                        if nargs_int < 0:
                            error_msg = "nargs cannot be negative"
                            raise ValueError(error_msg)
                    except ValueError:
                        error_msg = f"Invalid nargs value: {nargs}"
                        raise ValueError(error_msg) from None

            # Raise error if 'nargs' is neither int nor str
            else:
                error_msg = f"nargs must be an int or str, got {type(nargs)}"
                raise TypeError(error_msg)

        # Assign default value to 'const' for nargs='?' if not set
        if nargs == "?" and self.__argument.get("const") is None:
            if self.__original_type is bool:
                self.__argument["const"] = True
            else:
                self.__argument["const"] = "default_value"

        # Set default to empty list for '*' or '+' if not specified
        if nargs in ["*", "+"] and self.__argument.get("default") is None:
            self.__argument["default"] = []
