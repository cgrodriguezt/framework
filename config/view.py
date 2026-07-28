from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.view import View
from orionis.environment import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapView(View):

    # ----------------------------------------------------------------------------------
    # paths : list, optional
    # --- Directories searched for templates in priority order.
    # ----------------------------------------------------------------------------------
    paths: list = field(
        default_factory=lambda: Env.get("VIEW_PATHS", ["resources/views"]),
    )

    # ----------------------------------------------------------------------------------
    # cache_size : int, optional
    # --- Maximum compiled templates held in the LRU memory cache.
    # ----------------------------------------------------------------------------------
    cache_size: int = field(
        default_factory=lambda: int(Env.get("VIEW_CACHE_SIZE", 400)),
    )

    # ----------------------------------------------------------------------------------
    # cache_path : str | None, optional
    # --- Filesystem path for bytecode caching (None disables disk cache).
    # ----------------------------------------------------------------------------------
    cache_path: str | None = field(
        default_factory=lambda: Env.get("VIEW_CACHE_PATH", "storage/framework/views"),
    )

    # ----------------------------------------------------------------------------------
    # autoescape : bool, optional
    # --- Enable automatic HTML escaping of all template variables.
    # ----------------------------------------------------------------------------------
    autoescape: bool = field(
        default_factory=lambda: bool(Env.get("VIEW_AUTOESCAPE", True)),
    )
