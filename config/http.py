from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.http.entitites.cors import Cors
from orionis.foundation.config.http.entitites.http import HTTP
from orionis.foundation.config.http.entitites.proxies import HTTPProxies
from orionis.foundation.config.http.entitites.rate_limit import HTTPRateLimit
from orionis.foundation.config.http.entitites.security import HTTPSecurity
from orionis.services.environment.env import Env

@dataclass(frozen=True, kw_only=True)
class BootstrapHTTP(HTTP):

    # ==================================================================================
    # PROXIES
    # ==================================================================================

    proxies: HTTPProxies = field(
        default_factory=lambda: HTTPProxies(

            # --------------------------------------------------------------------------
            # trusted_proxies : list[str], optional
            # --- List of trusted proxy IP addresses or CIDR ranges.
            # --- Uses 'TRUSTED_PROXIES' env var or empty list if not set.
            # --------------------------------------------------------------------------

            trusted_proxies=Env.get("TRUSTED_PROXIES", []),
        ),
    )

    # ==================================================================================
    # SECURITY
    # ==================================================================================

    security: HTTPSecurity = field(
        default_factory=lambda: HTTPSecurity(

            # --------------------------------------------------------------------------
            # allowed_hosts : list[str] | Literal["*"], optional
            # --- List of allowed host names for request validation.
            # --- Entries may use a leading wildcard for subdomains
            # --- (e.g. '*.example.com'). Defaults to '*' to allow all hosts.
            # --------------------------------------------------------------------------

            allowed_hosts="*",
        ),
    )

    # ==================================================================================
    # RATE LIMIT
    # ==================================================================================

    rate_limit: HTTPRateLimit = field(
        default_factory=lambda: HTTPRateLimit(

            # --------------------------------------------------------------------------
            # rate_limit_enabled : bool, optional
            # --- Enable or disable global rate limiting.
            # --- Uses 'RATE_LIMIT_ENABLED' env var or False if not set.
            # --------------------------------------------------------------------------

            rate_limit_enabled=Env.get("RATE_LIMIT_ENABLED", False),

            # --------------------------------------------------------------------------
            # rate_limit_requests : int, optional
            # --- Maximum number of requests allowed per time window.
            # --- Uses 'RATE_LIMIT_REQUESTS' env var or 100 if not set.
            # --------------------------------------------------------------------------

            rate_limit_requests=int(Env.get("RATE_LIMIT_REQUESTS", 100)),

            # --------------------------------------------------------------------------
            # rate_limit_window_seconds : int, optional
            # --- Time window in seconds for rate limit counting.
            # --- Uses 'RATE_LIMIT_WINDOW' env var or 60 if not set.
            # --------------------------------------------------------------------------

            rate_limit_window_seconds=int(Env.get("RATE_LIMIT_WINDOW", 60)),
        ),
    )

    # ==================================================================================
    # CORS
    # ==================================================================================

    cors: Cors = field(
        default_factory=lambda: Cors(

            # --------------------------------------------------------------------------
            # allow_origins : list[str], optional
            # --- List of allowed origins. Use ["*"] to allow all. Defaults to ["*"].
            # --------------------------------------------------------------------------

            allow_origins=["*"],

            # --------------------------------------------------------------------------
            # allow_origin_regex : str | None, optional
            # --- Regex pattern to match allowed origins. Defaults to None.
            # --------------------------------------------------------------------------

            allow_origin_regex=None,

            # --------------------------------------------------------------------------
            # allow_methods : list[str], optional
            # --- List of allowed HTTP methods. Use ["*"] to allow all methods.
            # --------------------------------------------------------------------------

            allow_methods=["*"],

            # --------------------------------------------------------------------------
            # allow_headers : list[str], optional
            # --- List of allowed HTTP headers. Use ["*"] to allow all headers.
            # --------------------------------------------------------------------------

            allow_headers=["*"],

            # --------------------------------------------------------------------------
            # expose_headers : list[str], optional
            # --- List of headers exposed to the browser. Defaults to [].
            # --------------------------------------------------------------------------

            expose_headers=[],

            # --------------------------------------------------------------------------
            # allow_credentials : bool, optional
            # --- Allow credentials (cookies, authorization headers). Defaults to False.
            # --------------------------------------------------------------------------

            allow_credentials=False,

            # --------------------------------------------------------------------------
            # max_age : int | None, optional
            # --- Max time in seconds to cache preflight response. Defaults to 600.
            # --------------------------------------------------------------------------

            max_age=600,
        ),
    )
