from __future__ import annotations
from typing import ClassVar
from orionis.foundation.config.logging.enums import Level

class _IsValidLevel:
    """
    Validate if a value is a valid logging level.

    This validator checks if the provided value is a valid logging level.
    Accepted types are int, str, or Level enum.

    Attributes
    ----------
    _level_names : set[str]
        Set of valid logging level names.
    _level_values : set[int]
        Set of valid logging level integer values.
    """

    _level_names: ClassVar[set[str]] = {level.name for level in Level}
    _level_values: ClassVar[set[int]] = {level.value for level in Level}

    def __call__(self, value: Level | int | str) -> None:
        """
        Validate if the provided value is a valid logging level.

        Parameters
        ----------
        value : Level | int | str
            Value to validate as a logging level. Can be int, str, or Level enum.

        Returns
        -------
        None
            This method does not return a value. It raises an exception if
            validation fails.

        Raises
        ------
        ValueError
            If the value is not a valid logging level.
        TypeError
            If the value is not of an accepted type (int, str, or Level).
        """
        # Accept Level enum instances directly
        if isinstance(value, Level):
            return

        # Validate integer values
        if isinstance(value, int):
            if value not in self._level_values:
                error_msg = (
                    f"'level' must be one of {sorted(self._level_values)}, "
                    f"got {value}."
                )
                raise ValueError(error_msg)
            return

        # Validate string values
        if isinstance(value, str):
            name = value.strip().upper()
            if name not in self._level_names:
                error_msg = (
                    f"'level' must be one of {sorted(self._level_names)}, "
                    f"got '{value}'."
                )
                raise ValueError(error_msg)
            return

        # Raise TypeError for unsupported types
        error_msg = (
            f"'level' must be int, str, or Level enum, got {type(value).__name__}."
        )
        raise TypeError(error_msg)

# Exported singleton instance
IsValidLevel = _IsValidLevel()
