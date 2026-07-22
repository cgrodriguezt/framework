from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.config.cache.entities.memcached import Memcached
from orionis.foundation.config.cache.entities.memory import Memory
from orionis.foundation.config.cache.entities.redis import Redis
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.enums import Drivers
from orionis.environment import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapCache(Cache):

    # ----------------------------------------------------------------------------------
    # default : Drivers | str, optional
    # --- The default cache store driver. Defaults to the CACHE_STORE env var or FILE.
    # ----------------------------------------------------------------------------------
    default: Drivers | str = field(
        default_factory=lambda: Env.get("CACHE_STORE", Drivers.FILE),
    )

    # ----------------------------------------------------------------------------------
    # prefix : str, optional
    # --- Global key prefix applied to all cache entries.
    # ----------------------------------------------------------------------------------
    prefix: str = field(
        default_factory=lambda: Env.get("CACHE_PREFIX", ""),
    )

    # ----------------------------------------------------------------------------------
    # stores : Stores | dict, optional
    # --- Configuration for all available cache backends.
    # ----------------------------------------------------------------------------------
    stores: Stores | dict = field(
        default_factory=lambda: Stores(

            # --------------------------------------------------------------------------
            # File-based cache store (default driver)
            # --------------------------------------------------------------------------
            file=File(
                path=Env.get("CACHE_FILE_PATH", "storage/framework/cache/data"),
            ),

            # --------------------------------------------------------------------------
            # In-memory cache store (no persistence, process-scoped)
            # --------------------------------------------------------------------------
            memory=Memory(),

            # --------------------------------------------------------------------------
            # Redis cache store
            # --------------------------------------------------------------------------
            redis=Redis(
                endpoint=Env.get("REDIS_HOST", "127.0.0.1"),
                port=Env.get("REDIS_PORT", 6379),
                db=Env.get("REDIS_DB", 0),
                password=Env.get("REDIS_PASSWORD"),
            ),

            # --------------------------------------------------------------------------
            # Memcached cache store
            # --------------------------------------------------------------------------
            memcached=Memcached(
                endpoint=Env.get("MEMCACHED_HOST", "127.0.0.1"),
                port=Env.get("MEMCACHED_PORT", 11211),
            ),

        ),
    )
