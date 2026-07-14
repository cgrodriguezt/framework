from __future__ import annotations
from dataclasses import dataclass, field
from orionis.environment import Env
from orionis.foundation.config.http import (
    Cors,
    HTTP,
    HTTPProxies,
    HTTPRateLimit,
    HTTPSecurity,
)

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

            allowed_hosts=Env.get("ALLOWED_HOSTS", "*"),
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

            allow_origins=Env.get("CORS_ALLOW_ORIGINS", ["*"]),

            # --------------------------------------------------------------------------
            # allow_origin_regex : str | None, optional
            # --- Regex pattern to match allowed origins. Defaults to None.
            # --------------------------------------------------------------------------

            allow_origin_regex=Env.get("CORS_ALLOW_ORIGIN_REGEX", None),

            # --------------------------------------------------------------------------
            # allow_methods : list[str], optional
            # --- List of allowed HTTP methods. Use ["*"] to allow all methods.
            # --------------------------------------------------------------------------

            allow_methods=Env.get("CORS_ALLOW_METHODS", ["*"]),

            # --------------------------------------------------------------------------
            # allow_headers : list[str], optional
            # --- List of allowed HTTP headers. Use ["*"] to allow all headers.
            # --------------------------------------------------------------------------

            allow_headers=Env.get("CORS_ALLOW_HEADERS", ["*"]),

            # --------------------------------------------------------------------------
            # expose_headers : list[str], optional
            # --- List of headers exposed to the browser. Defaults to [].
            # --------------------------------------------------------------------------

            expose_headers=Env.get("CORS_EXPOSE_HEADERS", []),

            # --------------------------------------------------------------------------
            # allow_credentials : bool, optional
            # --- Allow credentials (cookies, authorization headers). Defaults to False.
            # --------------------------------------------------------------------------

            allow_credentials=Env.get("CORS_ALLOW_CREDENTIALS", False),

            # --------------------------------------------------------------------------
            # max_age : int | None, optional
            # --- Max time in seconds to cache preflight response. Defaults to 600.
            # --------------------------------------------------------------------------

            max_age=Env.get("CORS_MAX_AGE", 600),
        ),
    )
