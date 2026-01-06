from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.enums import Drivers
from orionis.services.environment.env import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapCache(Cache):

    # ----------------------------------------------------------------------------------
    # default : Drivers | str, optional
    # --- The default cache store driver. Can be a member of the Drivers enum or a
    #     string (e.g., 'memory', 'file'). Defaults to the value of the 'CACHE_STORE'
    #     environment variable or Drivers.FILE.
    # ----------------------------------------------------------------------------------
    default: Drivers | str = field(
        default_factory=lambda: Env.get("CACHE_STORE", Drivers.FILE),
    )

    # ----------------------------------------------------------------------------------
    # stores : Stores | dict, optional
    # --- Configuration for available cache stores. Accepts a Stores instance or a dict.
    #     Defaults to a file store at the path specified by 'CACHE_FILE_PATH' or
    #     'storage/framework/cache/data' if not set.
    # ----------------------------------------------------------------------------------
    stores: Stores | dict = field(
        default_factory=lambda: Stores(

            # --------------------------------------------------------------------------
            #  - Configuration for a file-based cache store.
            #  - Uses the File entity to define the path for cache data storage.
            #  - Defaults to 'storage/framework/cache/data' if not specified in the env
            # --------------------------------------------------------------------------
            file=File(
                path=Env.get("CACHE_FILE_PATH", "storage/framework/cache/data"),
            ),

        ),
    )
