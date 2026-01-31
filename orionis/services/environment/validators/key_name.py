from __future__ import annotations
import re

class __ValidateKeyName:

    # Regular expression pattern to match valid environment variable names
    _pattern = re.compile(r"^[A-Z][A-Z0-9_]*$")

    def __call__(self, key: object) -> str:
        """
        Validate that the provided environment variable name meets requirements.

        Parameters
        ----------
        key : object
            The environment variable name to validate.

        Returns
        -------
        str
            The validated environment variable name if it meets format
            requirements.

        Raises
        ------
        ValueError
            If the provided key is not a string or does not match the required
            format.
        """
        # Ensure the key is of type string
        if not isinstance(key, str):
            error_msg = (
                f"Environment variable name must be a string, got "
                f"{type(key).__name__}."
            )
            raise TypeError(error_msg)

        # Check if the key matches the required pattern for environment names
        if not self._pattern.fullmatch(key):
            error_msg = (
                f"Invalid environment variable name '{key}'. It must start "
                "with an uppercase letter, contain only uppercase letters, "
                "numbers, or underscores. Example: 'MY_ENV_VAR'."
            )
            raise ValueError(error_msg)

        # Return the validated key if all checks pass
        return key

# Instance to be used for key name validation
ValidateKeyName = __ValidateKeyName()
