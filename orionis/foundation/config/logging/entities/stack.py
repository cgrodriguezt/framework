from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.logging.enums import Level
from orionis.foundation.config.logging.validators import IsValidLevel, IsValidPath
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Stack(BaseEntity):
    """
    Represent the configuration for a logging stack.

    Parameters
    ----------
    path : str
        The file path where the log is stored.
    level : int | str | Level
        The logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Attributes
    ----------
    path : str
        The file path where the log is stored.
    level : int | str | Level
        The logging level.
    """

    path: str = field(
        default="storage/logs/stack.log",
        metadata={
            "description": "The file path where the log is stored.",
            "default": "storage/logs/stack.log",
        },
    )

    level: int | str | Level = field(
        default=Level.INFO.value,
        metadata={
            "description": (
                "The logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)."
            ),
            "default": Level.INFO.value,
        },
    )

    def __post_init__(self) -> None:
        """
        Validate the 'path' and 'level' attributes after dataclass initialization.

        Raises
        ------
        ValueError
            If 'path' is not a non-empty string, or if 'level' is not a valid type
            or value.
        TypeError
            If 'level' is of an unsupported type.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Call the superclass's __post_init__ method.
        super().__post_init__()

        # Validate 'path' using the IsValidPath validator.
        try:
            IsValidPath(self.path)
        except Exception as e:
            error_msg = f"Invalid path: {self.path}"
            raise ValueError(error_msg) from e

        # Validate 'level' using the IsValidLevel validator.
        try:
            IsValidLevel(self.level)
        except TypeError as e:
            error_msg = f"Invalid type for level: {self.level}"
            raise TypeError(error_msg) from e
        except Exception as e:
            error_msg = f"Invalid value for level: {self.level}"
            raise ValueError(error_msg) from e

        # Normalize the level value to its integer representation.
        if isinstance(self.level, Level):
            object.__setattr__(self, "level", self.level.value)
        elif isinstance(self.level, str):
            try:
                object.__setattr__(
                    self,
                    "level",
                    Level[self.level.strip().upper()].value,
                )
            except KeyError as e:
                error_msg = f"Invalid level string: {self.level}"
                raise ValueError(error_msg) from e
