import re
from typing import Any, Union
from orionis.services.environment.enums.cast_type import EnvCastType
from orionis.services.environment.exceptions.value import OrionisEnvironmentValueError

class __ValidateTypes:

    def __call__(self, value: Union[str, int, float, bool, list, dict, tuple, set], type_hint: str | EnvCastType = None) -> str:

        # Ensure the value is a valid type.
        if not isinstance(value, (str, int, float, bool, list, dict, tuple, set)):
            raise OrionisEnvironmentValueError(
                f"Unsupported value type: {type(value).__name__}. Allowed types are str, int, float, bool, list, dict, tuple, set."
            )

        # If a type hint is provided, ensure it is valid.
        if type_hint and not isinstance(type_hint, (str, EnvCastType)):
            raise OrionisEnvironmentValueError(
                f"Type hint must be a string or EnvCastType, got {type(type_hint).__name__}."
            )

        # If type_hint is provided, convert it to a string if it's an EnvCastType.
        if type_hint:

            # If type_hint is a string, convert it to EnvCastType if valid.
            if isinstance(type_hint, str):
                try:
                    type_hint = EnvCastType[type_hint.upper()].value
                except KeyError:
                    raise OrionisEnvironmentValueError(
                        f"Invalid type hint: {type_hint}. Allowed types are {[e.value for e in EnvCastType]}"
                    )
            elif isinstance(type_hint, EnvCastType):
                type_hint = type_hint.value

        # If no type hint is provided, use the type of the value.
        else:
            type_hint = type(value).__name__.lower()

        # Return the type hint as a string.
        return type_hint


# Instance to be used for key name validation
ValidateTypes = __ValidateTypes()