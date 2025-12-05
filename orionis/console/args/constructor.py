import re
from typing import Any, ClassVar
from orionis.console.args.argument import CLIArgument
from orionis.console.enums.actions import ArgumentAction
from orionis.support.patterns.final.meta import Final

class CLIArgumentConstructor(metaclass=Final):

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
        # Store the argument as a dictionary for further processing
        self.__argument = argument.toDict()

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
                error_msg = "Name contains invalid characters"
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

    def __validateAndAssignFlags(self) -> None:
        """
        Validate and assign the flags for the argument based on its properties.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Validate flags - must be provided and non-empty
        if not self.__argument.get("flags"):
            error_msg = "Flags list cannot be empty"
            raise ValueError(error_msg)

        # Convert single string flag to list for consistency
        if isinstance(self.__argument.get("flags"), str):
            self.__argument["flags"] = [self.__argument.get("flags")]

        # Ensure flags is a list
        if not isinstance(self.__argument.get("flags"), list):
            error_msg = "Flags must be provided as a list of strings"
            raise TypeError(error_msg)

        # Validate each flag format and ensure they're strings
        for flag in self.__argument.get("flags"):
            if not isinstance(flag, str):
                error_msg = f"Flag '{flag}' is not a string"
                raise TypeError(error_msg)
            if not self.__is_positional_argument and not flag.startswith("-"):
                error_msg = f"Each flag must start with '-', but got '{flag}'"
                raise ValueError(error_msg)

        # Check for duplicate flags
        if len(set(self.__argument.get("flags"))) != len(self.__argument.get("flags")):
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

            # Try to convert string to ArgumentAction enum
            try:
                self.__argument["action"] = ArgumentAction(action)
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
        Validate and assign the type of the argument.

        Checks if the type is a valid Python type or custom type class.
        Prohibits boolean types for positional arguments.
        Stores the original type for further validation.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Check if the argument type is a valid Python type or custom type class
        if not isinstance(self.__argument.get("type"), type):
            error_msg = "Type must be a valid Python type or custom type class"
            raise TypeError(error_msg)

        # Prohibit positional arguments from being of boolean type
        if self.__argument.get("type") is bool and self.__is_positional_argument:
            error_msg = "Boolean type cannot be used with positional arguments"
            raise ValueError(error_msg)

        # Store the original type for further validation
        self.__original_type = self.__argument.get("type")

    def __determineIfOptional(self) -> None:
        """
        Determine if the argument is optional based on its flags.

        An argument is considered optional if any flag starts with '-'.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Check if any flag starts with '-' to determine if the argument is optional
        self.__is_optional = any(
            flag.startswith("-") for flag in self.__argument.get("flags")
        )

    def __handleOptionalBoolean(self) -> None: # NOSONAR
        """
        Handle optional boolean and list arguments, and set appropriate action and type.

        For optional boolean arguments, set the action to STORE_FALSE or STORE_TRUE
        based on the default value, and set the type to None. For list arguments,
        set nargs and type accordingly. For count action, set type and default.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Check if the original type is boolean

        if self.__original_type is bool:

            # Check if the argument is optional (has a flag starting with '-')
            if self.__is_optional:

                # Set action based on the default value
                if self.__argument.get("default"):
                    self.__argument["action"] = ArgumentAction.STORE_FALSE.value
                else:
                    self.__argument["action"] = ArgumentAction.STORE_TRUE.value

                # Set type to None for optional boolean arguments
                self.__argument["type"] = None

        # Special handling for list types
        elif self.__original_type is list:

            # Set nargs if not already specified

            if self.__argument.get("nargs") is None:
                self.__argument["nargs"] = "+" if self.__is_optional else "*"

            # Set type to str for list arguments
            self.__argument["type"] = str

        # Handle count action
        elif self.__argument.get("action") == ArgumentAction.COUNT.value:

            # Set type to None for count action
            self.__argument["type"] = None

            # Set default to 0 if not already specified
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
        # Handle STORE_CONST and APPEND_CONST actions
        if self.__argument.get("action") in (
            ArgumentAction.STORE_CONST.value,
            ArgumentAction.APPEND_CONST.value,
        ):

            # Assign default value to 'const' if not provided
            if self.__argument.get("const") is None:

                # For boolean type, set const to True
                if self.__original_type is bool:
                    self.__argument["const"] = True

                # For integer type, set const to 1
                elif self.__original_type is int:
                    self.__argument["const"] = 1

                # For string type, set const to "default_value"
                elif self.__original_type is str:
                    self.__argument["const"] = "default_value"

                # For other types, set const to True
                else:
                    self.__argument["const"] = True

            # Set type to None for const actions
            self.__argument["type"] = None

        # Handle VERSION action
        if self.__argument.get("action") == ArgumentAction.VERSION.value:

            # Set type to None for version action
            self.__argument["type"] = None

            # Assign default version if not provided
            if self.__argument.get("version") is None:
                self.__argument["version"] = "1.0.0"

        # Handle HELP action
        if self.__argument.get("action") == ArgumentAction.HELP.value:

            # Set type to None for help action
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
        Generate and assign 'metavar' and 'dest' properties for the argument.

        This method sets the 'metavar' property based on the argument's action,
        type, and positional status. It also generates the 'dest' property,
        ensuring it is a valid Python identifier. Adjustments are made for
        special actions such as VERSION.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Generate 'metavar' if the action does not ignore it
        if self.__argument.get("action") in self.ACTIONS_IGNORING_METAVAR:
            self.__argument["metavar"] = None

        # Generate 'metavar' for non-boolean, non-positional arguments
        elif (
            self.__argument.get("metavar") is None
            and self.__original_type is not bool
            and not self.__is_positional_argument
        ):
            metavar = self.__primary_flag.lstrip("-").upper().replace("-", "_")
            self.__argument["metavar"] = metavar

        # Validate 'metavar' type
        if (
            self.__argument.get("metavar") is not None
            and not isinstance(self.__argument.get("metavar"), str)
        ):

            # Ensure 'metavar' is a string
            error_msg = "Metavar must be a string"
            raise TypeError(error_msg)

        # Generate 'dest' if not already set
        if self.__argument.get("dest") is None:

            # Assign 'dest' for positional arguments
            if self.__is_positional_argument:
                dest = str(self.__argument.get("name")).replace("-", "_")\
                                                       .replace(".", "_")

            # Assign 'dest' for optional arguments
            else:
                dest = self.__primary_flag.lstrip("-")\
                                          .replace("-", "_")\
                                          .replace(".", "_")

            self.__argument["dest"] = dest

        # Adjust 'dest' for VERSION action
        if (
            self.__argument.get("action") == ArgumentAction.VERSION.value
            and "version" not in self.__argument.get("dest")
        ):
            self.__argument["dest"] = "version"

        # Validate 'dest' type
        if not isinstance(self.__argument.get("dest"), str):

            # Ensure 'dest' is a string
            error_msg = "Destination (dest) must be a string"
            raise TypeError(error_msg)

        # Validate 'dest' as a Python identifier
        if not str(self.__argument.get("dest")).isidentifier():

            # Ensure 'dest' is a valid identifier
            error_msg = f"Destination '{self.dest}' is not a valid Python identifier"
            raise ValueError(error_msg)

    def __validateAndAssignChoices(self) -> None:
        """
        Validate and assign the 'choices' attribute for the argument.

        Ensures that 'choices' is a list and that all elements match the original
        argument type.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Retrieve the choices from the argument dictionary
        choices = self.__argument.get("choices")

        # If choices are provided, validate their type and contents
        if choices is not None:

            # Ensure choices is a list
            if not isinstance(choices, list):
                error_msg = "Choices must be provided as a list"
                raise TypeError(error_msg)

            # Ensure all choices match the original argument type
            if not all(isinstance(choice, self.__original_type) for choice in choices):
                error_msg = (
                    f"All choices must be of type {self.__original_type.__name__}"
                )
                raise TypeError(error_msg)

    def __validateRequiredType(self) -> None:
        """
        Validate that the 'required' field is a boolean value.

        Raises
        ------
        TypeError
            If the 'required' field is not a boolean.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Check if the 'required' field is a boolean value
        if not isinstance(self.__argument.get("required"), bool):
            error_msg = "Required field must be a boolean value (True or False)"
            raise TypeError(error_msg)

    def __assignDefaultHelp(self) -> None:
        """
        Assign default help text to the argument if not provided.

        Adds a default help message based on the primary flag if the 'help'
        attribute is missing. Validates that the help text is a string.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Assign default help message if 'help' is not set
        if self.__argument.get("help") is None:

            # Clean the primary flag for display in help message
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

        Check that 'nargs' is a valid integer or string value. Assign a default
        value to 'const' if 'nargs' is '?' and 'const' is not set.

        Returns
        -------
        None
            Always returns None.
        """
        # Get the value of 'nargs' from the argument dictionary
        nargs = self.__argument.get("nargs")

        # Validate 'nargs' if it is provided
        if nargs is not None:

            # If 'nargs' is an integer, ensure it is non-negative
            if isinstance(nargs, int):
                if nargs < 0:
                    error_msg = "nargs cannot be negative"
                    raise ValueError(error_msg)

            # If 'nargs' is a string, check for valid values or convert to int
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

        # Assign default value to 'const' if 'nargs' is '?' and 'const' is not set
        if nargs == "?" and self.__argument.get("const") is None:

            # If the original type is bool, set 'const' to True
            if self.__original_type is bool:
                self.__argument["const"] = True

            # Otherwise, set 'const' to "default_value"
            else:
                self.__argument["const"] = "default_value"
