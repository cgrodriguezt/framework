from dataclasses import dataclass
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.enums import Drivers
from orionis.services.environment.env import Env

@dataclass
class BootstrapCache(Cache):

    # -------------------------------------------------------------------------
    # default : str | Drivers
    #     - The default cache store driver.+
    #     - Loaded from environment variable 'CACHE_STORE' or defaults to Drivers.MEMORY.
    # -------------------------------------------------------------------------
    default = Env.get("CACHE_STORE", Drivers.MEMORY)

    # -------------------------------------------------------------------------
    # stores : dict | Stores
    #     - The configuration for available cache stores.
    #     - Contains a 'file' store with a path loaded from environment variable 'CACHE_FILE_PATH' or defaults to 'storage/framework/cache/data'.
    #     - Other stores can be added as needed.
    # -------------------------------------------------------------------------
    stores = Stores(

        # ---------------------------------------------------------------------
        # file : File
        #     - Configuration for a file-based cache store.
        #     - Uses the File entity to define the path for cache data storage.
        #     - Defaults to 'storage/framework/cache/data' if not specified in the environment.
        # ---------------------------------------------------------------------

        file = File(
            path = Env.get("CACHE_FILE_PATH", "storage/framework/cache/data")
        )
    )