from dataclasses import dataclass, field
from orionis.luminate.config.cache.entities.file import File
from orionis.luminate.config.cache.entities.stores import Stores
from orionis.luminate.config.cache.enums.drivers import Drivers
from orionis.luminate.config.exceptions.integrity_exception import OrionisIntegrityException
from orionis.luminate.services.environment import Env

@dataclass
class Cache:
    """
    Represents the cache configuration for the application.
    Attributes:
        default (Drivers | str): The default cache storage type. Can be a member of the Drivers enum or a string
            (e.g., 'memory', 'file'). Defaults to the value of the 'CACHE_STORE' environment variable or Drivers.MEMORY.
        stores (Stores): The configuration for available cache stores. Defaults to a Stores instance with a file store
            at the path specified by the 'CACHE_PATH' environment variable or "storage/framework/cache/data".
    Methods:
        __post_init__():
            - Validates that 'default' is either a Drivers enum member or a string.
            - Converts 'default' from string to Drivers enum if necessary.
            - Validates that 'stores' is an instance of Stores.
    """

    default: Drivers | str = field(
        default=Env.get("CACHE_STORE", Drivers.MEMORY),
        metadata={
            "description": "The default cache storage type (e.g., 'memory' or 'file').",
            "type": Drivers,
        },
    )

    stores: Stores = field(
        default_factory=lambda: Stores(
            file=File(
                path=Env.get("CACHE_PATH", "storage/framework/cache/data")
            )
        )
    )

    def __post_init__(self):
        """
        Post-initialization processing to ensure the cache configuration is set correctly.
        """
        # Ensure the default cache store is valid
        if not isinstance(self.default, (Drivers, str)):
            raise OrionisIntegrityException("The default cache store must be an instance of Drivers or a string.")

        # Convert string to Drivers enum if applicable
        if isinstance(self.default, str):
            value = self.default.upper().strip()
            if value not in Drivers._member_names_:
                raise OrionisIntegrityException(f"Invalid cache driver: {self.default}. Must be one of {Drivers._member_names_}.")
            else:
                self.default = getattr(Drivers, value)

        # Ensure the stores attribute is an instance of Stores
        if not isinstance(self.stores, Stores):
            raise OrionisIntegrityException("The stores must be an instance of Stores.")