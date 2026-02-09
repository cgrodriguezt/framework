from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.enums import Drivers
from orionis.services.environment.env import Env
from orionis.support.entities.base import BaseEntity

@dataclass(frozen=True, kw_only=True)
class Cache(BaseEntity):
    """
    Represent the cache configuration for the application.

    Parameters
    ----------
    default : Drivers | str
        The default cache storage type. Can be a member of the Drivers enum or a
        string (e.g., 'memory', 'file'). Defaults to the value of the
        'CACHE_STORE' environment variable or Drivers.MEMORY.
    stores : Stores | dict
        The configuration for available cache stores. Defaults to a Stores
        instance with a file store at the path specified by the 'CACHE_PATH'
        environment variable or "storage/framework/cache/data".
    """

    # ruff: noqa: PLW0108

    default: Drivers | str = field(
        default_factory=lambda: Env.get("CACHE_STORE", Drivers.FILE.value),
        metadata={
            "description": (
                "The default cache storage type. Can be a member of the Drivers "
                "enum or a string (e.g., 'memory', 'file')."
            ),
            "default": Drivers.FILE.value,
        },
    )

    stores: Stores | dict = field(
        default_factory=lambda: Stores(),
        metadata={
            "description": (
                "The configuration for available cache stores. Defaults to a file "
                "store at the specified path."
            ),
            "default": lambda: Stores().toDict(),
        },
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the cache configuration after initialization.

        Parameters
        ----------
        self : Cache
            The instance of the Cache class.

        Returns
        -------
        None
            This method modifies the instance in place and returns None.

        Raises
        ------
        ValueError
            If `default` is not a valid driver.
        TypeError
            If `stores` is not an instance of `Stores` or dict.

        Notes
        -----
        Ensures that the `default` attribute is either an instance of `Drivers`
        or a string representing a valid driver name. Converts `default` from
        string to Drivers enum if necessary. Ensures that the `stores`
        attribute is an instance of `Stores`.
        """
        # Call the superclass post-initialization
        super().__post_init__()

        # Ensure 'default' is either a Drivers enum member or a string
        if not isinstance(self.default, (Drivers, str)):
            error_msg = (
                "The default cache store must be an instance of Drivers or a string."
            )
            raise TypeError(error_msg)

        # Validate and normalize the driver string if necessary
        options_drivers = Drivers._member_names_
        if isinstance(self.default, str):
            _value = self.default.upper().strip()
            if _value not in options_drivers:
                error_msg = (
                    f"Invalid cache driver: {self.default}. Must be one of "
                    f"{options_drivers!s}."
                )
                raise ValueError(error_msg)
            # Convert string to Drivers enum value
            object.__setattr__(self, "default", Drivers[_value].value)
        else:
            # Use the enum value directly
            object.__setattr__(self, "default", self.default.value)

        # Ensure 'stores' is an instance of Stores or dict
        if not isinstance(self.stores, (Stores, dict)):
            error_msg = (
                "The stores configuration must be an instance of "
                "Stores or a dictionary."
            )
            raise TypeError(error_msg)

        # Convert dictionary to Stores instance if needed
        if isinstance(self.stores, dict):
            object.__setattr__(self, "stores", Stores(**self.stores))
