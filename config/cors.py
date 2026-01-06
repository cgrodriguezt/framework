from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.cors.entities.cors import Cors

@dataclass(frozen=True, kw_only=True)
class BootstrapCors(Cors):

    # ----------------------------------------------------------------------------------
    # allow_origins : list[str], optional
    # --- List of allowed origins. Use ["*"] to allow all origins. Defaults to ["*"].
    # --- If you want to restrict origins, provide a list of allowed origin strings.
    # ----------------------------------------------------------------------------------
    allow_origins: list[str] = field(
        default_factory=lambda: ["*"],
    )

    # ----------------------------------------------------------------------------------
    # allow_origin_regex : str | None, optional
    # --- Regex pattern to match allowed origins. Defaults to None (no regex matching).
    # --- If set, only origins matching the regex are allowed. Overrides allow_origins.
    # ----------------------------------------------------------------------------------
    allow_origin_regex: str | None = field(
        default=None,
    )

    # ----------------------------------------------------------------------------------
    # allow_methods : list[str], optional
    # --- List of allowed HTTP methods. Use ["*"] to allow all methods.
    #     Defaults to ["*"].
    # --- To restrict, provide a list of allowed HTTP method names (["GET", "POST"]).
    # ----------------------------------------------------------------------------------
    allow_methods: list[str] = field(
        default_factory=lambda: ["*"],
    )

    # ----------------------------------------------------------------------------------
    # allow_headers : list[str], optional
    # --- List of allowed HTTP headers. Use ["*"] to allow all headers.
    #     Defaults to ["*"].
    # --- To restrict, provide a list of allowed header names (e.g., ["Content-Type"]).
    # ----------------------------------------------------------------------------------
    allow_headers: list[str] = field(
        default_factory=lambda: ["*"],
    )

    # ----------------------------------------------------------------------------------
    # expose_headers : list[str], optional
    # --- List of headers exposed to the browser. Defaults to an empty list ([]).
    # --- Specify headers that can be accessed by the client in the response.
    # ----------------------------------------------------------------------------------
    expose_headers: list[str] = field(
        default_factory=list,
    )

    # ----------------------------------------------------------------------------------
    # allow_credentials : bool, optional
    # --- Allow credentials (cookies, authorization headers, etc.). Defaults to False.
    # --- Set to True to allow credentials in cross-origin requests.
    # ----------------------------------------------------------------------------------
    allow_credentials: bool = field(
        default=False,
    )

    # ----------------------------------------------------------------------------------
    # max_age : int | None, optional
    # --- Max time in seconds to cache preflight request. Defaults to 600 seconds.
    # --- Set to None to disable caching of preflight responses.
    # ----------------------------------------------------------------------------------
    max_age: int | None = field(
        default=600,
    )
