from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.logging.entities.chunked import Chunked
from orionis.foundation.config.logging.entities.daily import Daily
from orionis.foundation.config.logging.entities.hourly import Hourly
from orionis.foundation.config.logging.entities.monthly import Monthly
from orionis.foundation.config.logging.entities.stack import Stack
from orionis.foundation.config.logging.entities.weekly import Weekly
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Channels(BaseEntity):
    """
    Represent the available logging channels and their configurations.

    Attributes
    ----------
    stack : Stack | dict
        Configuration for stack log channel.
    hourly : Hourly | dict
        Configuration for hourly log rotation.
    daily : Daily | dict
        Configuration for daily log rotation.
    weekly : Weekly | dict
        Configuration for weekly log rotation.
    monthly : Monthly | dict
        Configuration for monthly log rotation.
    chunked : Chunked | dict
        Configuration for chunked log file storage.
    """

    # ruff: noqa: C901

    stack: Stack | dict = field(
        default_factory=lambda: Stack(),
        metadata={
            "description": "Configuration for stack log channel.",
            "default": lambda: Stack().toDict(),
        },
    )

    hourly: Hourly | dict = field(
        default_factory=lambda: Hourly(),
        metadata={
            "description": "Configuration for hourly log rotation.",
            "default": lambda: Hourly().toDict(),
        },
    )

    daily: Daily | dict = field(
        default_factory=lambda: Daily(),
        metadata={
            "description": "Configuration for daily log rotation.",
            "default": lambda: Daily().toDict(),
        },
    )

    weekly: Weekly | dict = field(
        default_factory=lambda: Weekly(),
        metadata={
            "description": "Configuration for weekly log rotation.",
            "default": lambda: Weekly().toDict(),
        },
    )

    monthly: Monthly | dict = field(
        default_factory=lambda: Monthly(),
        metadata={
            "description": "Configuration for monthly log rotation.",
            "default": lambda: Monthly().toDict(),
        },
    )

    chunked: Chunked | dict = field(
        default_factory=lambda: Chunked(),
        metadata={
            "description": "Configuration for chunked log file storage.",
            "default": lambda: Chunked().toDict(),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and convert channel attributes to their expected types.

        Ensures that each channel attribute is either an instance of its
        expected class or a dictionary. If a dictionary is provided, it is
        converted to the corresponding class instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Call the superclass post-initialization
        super().__post_init__()

        # Validate and convert `stack` attribute
        if not isinstance(self.stack, (Stack, dict)):
            error_msg = (
                "The 'stack' property must be an instance of Stack or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.stack, dict):
            object.__setattr__(self, "stack", Stack(**self.stack))

        # Validate and convert `hourly` attribute
        if not isinstance(self.hourly, (Hourly, dict)):
            error_msg = (
                "The 'hourly' property must be an instance of Hourly or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.hourly, dict):
            object.__setattr__(self, "hourly", Hourly(**self.hourly))

        # Validate and convert `daily` attribute
        if not isinstance(self.daily, (Daily, dict)):
            error_msg = (
                "The 'daily' property must be an instance of Daily or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.daily, dict):
            object.__setattr__(self, "daily", Daily(**self.daily))

        # Validate and convert `weekly` attribute
        if not isinstance(self.weekly, (Weekly, dict)):
            error_msg = (
                "The 'weekly' property must be an instance of Weekly or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.weekly, dict):
            object.__setattr__(self, "weekly", Weekly(**self.weekly))

        # Validate and convert `monthly` attribute
        if not isinstance(self.monthly, (Monthly, dict)):
            error_msg = (
                "The 'monthly' property must be an instance of Monthly or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.monthly, dict):
            object.__setattr__(self, "monthly", Monthly(**self.monthly))

        # Validate and convert `chunked` attribute
        if not isinstance(self.chunked, (Chunked, dict)):
            error_msg = (
                "The 'chunked' property must be an instance of Chunked or a dictionary."
            )
            raise TypeError(error_msg)
        if isinstance(self.chunked, dict):
            object.__setattr__(self, "chunked", Chunked(**self.chunked))
