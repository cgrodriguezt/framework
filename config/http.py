from __future__ import annotations
from dataclasses import dataclass, field
from orionis.foundation.config.http.entitites.cors import Cors
from orionis.foundation.config.http.entitites.http import HTTP
from orionis.foundation.config.http.entitites.proxies import HTTPProxies
from orionis.foundation.config.http.entitites.proxy_strategy import (
    ProxyStrategy as ProxyStrategyEntity,
)
from orionis.foundation.config.http.entitites.rate_limit import HTTPRateLimit
from orionis.foundation.config.http.entitites.request import HTTPRequest
from orionis.foundation.config.http.entitites.security import HTTPSecurity
from orionis.foundation.config.http.enums.strategies import ProxyStrategy
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

            # --------------------------------------------------------------------------
            # proxy_strategy : ProxyStrategy | str, optional
            # --- Determines how client IP and scheme are resolved from proxy headers.
            # --- Uses 'PROXY_STRATEGY' env var or 'standard' if not set.
            # --------------------------------------------------------------------------

            proxy_strategy=Env.get("PROXY_STRATEGY", ProxyStrategy.STANDARD),

            # --------------------------------------------------------------------------
            # proxy_strategies : dict[str, ProxyStrategyEntity], optional
            # --- Mapping of proxy strategy names to their header configurations.
            # --- Includes built-in strategies: standard, nginx, cloudflare, aws, fastly.
            # --------------------------------------------------------------------------

            proxy_strategies={
                "standard": ProxyStrategyEntity(
                    ip_header="x-forwarded-for",
                    proto_header="x-forwarded-proto",
                ),
                "nginx": ProxyStrategyEntity(
                    ip_header="x-real-ip",
                    proto_header="x-forwarded-proto",
                ),
                "cloudflare": ProxyStrategyEntity(
                    ip_header="cf-connecting-ip",
                    proto_header="x-forwarded-proto",
                ),
                "aws": ProxyStrategyEntity(
                    ip_header="x-forwarded-for",
                    proto_header="x-forwarded-proto",
                ),
                "fastly": ProxyStrategyEntity(
                    ip_header="fastly-client-ip",
                    proto_header="x-forwarded-proto",
                ),
            },
        ),
    )

    # ==================================================================================
    # SECURITY
    # ==================================================================================

    security: HTTPSecurity = field(
        default_factory=lambda: HTTPSecurity(

            # --------------------------------------------------------------------------
            # validate_headers : bool, optional
            # --- Whether to validate incoming HTTP headers for security.
            # --- Enables CRLF injection prevention and header duplication checks.
            # --------------------------------------------------------------------------

            validate_headers=True,

            # --------------------------------------------------------------------------
            # max_header_size : int, optional
            # --- Maximum allowed size for individual HTTP headers in bytes.
            # --- Defaults to 8192 bytes (8 KB). Applies to each header separately.
            # --------------------------------------------------------------------------

            max_header_size=8192,

            # --------------------------------------------------------------------------
            # block_multiple_host_headers : bool, optional
            # --- Whether to block requests with multiple Host headers.
            # --- Multiple Host headers can pose a security risk.
            # --------------------------------------------------------------------------

            block_multiple_host_headers=True,

            # --------------------------------------------------------------------------
            # allowed_hosts : list[str] | Literal["*"], optional
            # --- List of allowed host names for request validation.
            # --- Defaults to '*' to allow all hosts.
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
    # REQUEST
    # ==================================================================================

    request: HTTPRequest = field(
        default_factory=lambda: HTTPRequest(

            # --------------------------------------------------------------------------
            # allowed_content_types : list[str] | Literal["*"], optional
            # --- List of allowed Content-Type headers for incoming requests.
            # --- Defaults to '*' to allow all content types.
            # --------------------------------------------------------------------------

            allowed_content_types="*",

            # --------------------------------------------------------------------------
            # max_content_length : int | None, optional
            # --- Maximum allowed request body size in bytes.
            # --- Uses 'MAX_CONTENT_LENGTH' env var or 10 MB if not set.
            # --------------------------------------------------------------------------

            max_content_length=int(Env.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)),

            # --------------------------------------------------------------------------
            # enable_method_override : bool, optional
            # --- Enable or disable HTTP method override via header.
            # --- Uses 'METHOD_OVERRIDE' env var or True if not set.
            # --------------------------------------------------------------------------

            enable_method_override=Env.get("METHOD_OVERRIDE", True),

            # --------------------------------------------------------------------------
            # method_override_header : str, optional
            # --- Header name used for HTTP method override.
            # --- Defaults to 'x-http-method-override'.
            # --------------------------------------------------------------------------

            method_override_header="x-http-method-override",
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
