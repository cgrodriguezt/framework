from __future__ import annotations
from dataclasses import dataclass, field
from datetime import time
from orionis.foundation.config.logging.enums import Level
from orionis.foundation.config.logging.validators import IsValidLevel, IsValidPath
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Daily(BaseEntity):
    """
    Represent the configuration for daily log file rotation.

    Attributes
    ----------
    path : str
        The file path where the log is stored.
    level : int | str | Level
        The logging level (e.g., 'info', 'error', 'debug').
    retention_days : int
        The number of days to retain log files before deletion.
    at : time | str
        The time of day when the log rotation should occur.
    """

    path: str = field(
        default="storage/logs/daily_{suffix}.log",
        metadata={
            "description": "The file path where the log is stored.",
            "default": "storage/logs/daily_{suffix}.log",
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

    retention_days: int = field(
        default=7,
        metadata={
            "description": (
                "The number of days to retain log files before deletion."
            ),
            "default": 7,
        },
    )

    at: time = field(
        default_factory=lambda: time(0, 0),
        metadata={
            "description": (
                "The time of day when the log rotation should occur."
            ),
            "default": time(0, 0),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize attributes after dataclass initialization.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return a value. It validates and normalizes
            instance attributes after initialization.
        """
        # Call the superclass post-init method for base validation
        super().__post_init__()

        # Validate 'path' using the IsValidPath validator
        IsValidPath(self.path, suffix=True)

        # Validate 'level' using the IsValidLevel validator
        IsValidLevel(self.level)

        # Normalize 'level' to integer value if necessary
        if isinstance(self.level, Level):
            object.__setattr__(self, "level", self.level.value)
        elif isinstance(self.level, str):
            try:
                object.__setattr__(
                    self,
                    "level",
                    Level[self.level.strip().upper()].value,
                )
            except KeyError:
                error_msg = (
                    "'level' must be a valid Level name, got "
                    f"'{self.level}'."
                )
                raise KeyError(error_msg) from KeyError

        # Ensure 'retention_days' is an integer and within allowed range
        if not isinstance(self.retention_days, int):
            error_msg = (
                "'retention_days' must be an integer, got "
                f"{type(self.retention_days).__name__}."
            )
            raise TypeError(error_msg)
        maximum_retention = 90
        if not (1 <= self.retention_days <= maximum_retention):
            error_msg = (
                f"'retention_days' must be between 1 and {maximum_retention}, "
                f"got {self.retention_days}."
            )
            raise ValueError(error_msg)

        # Validate 'at' is strictly a time instance
        if isinstance(self.at, str):
            try:
                at_time = time.fromisoformat(self.at)
                object.__setattr__(self, "at", at_time)
            except ValueError:
                error_msg = (
                    "'at' string must be in HH:MM:SS format, got "
                    f"'{self.at}'."
                )
                raise ValueError(error_msg) from ValueError

        if not isinstance(self.at, time):
            error_msg = (
                "'at' must be a datetime.time instance, "
                f"got {type(self.at).__name__}."
            )
            raise TypeError(error_msg)
