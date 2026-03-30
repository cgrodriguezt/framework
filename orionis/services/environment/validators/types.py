from __future__ import annotations
from orionis.services.environment.enums.value_type import EnvironmentValueType

class __ValidateTypes:

    def __call__(
        self,
        *,
        value: str | float | bool | list | dict | tuple | set,
        type_hint: str | EnvironmentValueType | None = None,
    ) -> str:
        """
        Validate and determine the type of a given value.

        Parameters
        ----------
        value : str, int, float, bool, list, dict, tuple, or set
            The value whose type is to be validated and determined.
        type_hint : str or EnvironmentValueType, optional
            An optional type hint specifying the expected type. Can be a string
            or an EnvironmentValueType.

        Returns
        -------
        str
            The determined type as a string, either from the type hint or
            inferred from the value.

        Raises
        ------
        TypeError
            If value type is unsupported or type_hint has invalid type.
        RuntimeError
            If type_hint is not a valid EnvironmentValueType.
        """
        # Validate that the value is of a supported type
        if not isinstance(value, (str, int, float, bool, list, dict, tuple, set)):
            error_msg = (
                f"Unsupported value type: {type(value).__name__}. "
                f"Allowed types are str, int, float, bool, list, dict, tuple, set."
            )
            raise TypeError(error_msg)

        # Validate type hint if provided (use 'is not None' to avoid skipping
        # validation for falsy but invalid values such as 0 or empty string)
        if type_hint is not None and not isinstance(type_hint, (str, EnvironmentValueType)):
            error_msg = (
                f"Type hint must be a string or EnvironmentValueType, "
                f"got {type(type_hint).__name__}."
            )
            raise TypeError(error_msg)

        # Process type hint if provided and not None
        if type_hint is not None:
            # Convert type hint to standardized string value
            try:
                if isinstance(type_hint, str):
                    type_hint = EnvironmentValueType[type_hint.upper()].value
                elif isinstance(type_hint, EnvironmentValueType):
                    type_hint = type_hint.value

            # Handle invalid type hint values
            except KeyError:
                allowed_types = [e.value for e in EnvironmentValueType]
                error_msg = (
                    f"Invalid type hint: {type_hint}. "
                    f"Allowed types are: {allowed_types}"
                )
                raise RuntimeError(error_msg) from None

        # Use inferred type if no type hint provided
        else:
            type_hint = type(value).__name__.lower()

        # Return the determined type as string
        return type_hint

# Instance to be used for key name validation
ValidateTypes = __ValidateTypes()
