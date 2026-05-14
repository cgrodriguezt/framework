from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.foundation.config.http.entitites.rate_limit import HTTPRateLimit
from orionis.http.layer.store.memory_rate_limit import MemoryRateLimitStore

if TYPE_CHECKING:
    from orionis.http.adapters.request.contracts.transport import TransportAdapter
    from orionis.http.default.contracts.responses import IDefaultResponses
    from orionis.http.response import Response

class RateLimitMiddleware:

    def __init__(
        self,
        config: dict,
        default_responses: IDefaultResponses,
    ) -> None:
        """Initialize the middleware with the given rate-limit configuration.

        Parameters
        ----------
        config : dict
            A dictionary whose keys must match ``HTTPRateLimit`` fields.
        default_responses : IDefaultResponses
            Predefined default responses for common HTTP errors.

        Returns
        -------
        None
        """
        self.__config = HTTPRateLimit(**config)
        self.__rate_limit_enabled = self.__config.rate_limit_enabled
        self.__rate_limit_requests = self.__config.rate_limit_requests
        self.__rate_limit_window_seconds = (
            self.__config.rate_limit_window_seconds
        )
        self.__store = MemoryRateLimitStore()
        self.__default_responses = default_responses

    async def handle(
        self,
        adapter: TransportAdapter,
    ) -> Response | None:
        """Enforce the sliding-window rate limit for the incoming request.

        Skips enforcement when rate limiting is disabled or when the
        client IP cannot be resolved.  Returns a ``429`` response on
        the first request that exceeds the configured quota, or
        ``None`` when the request is within the allowed limit.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport abstraction providing client IP and header
            negotiation helpers.

        Returns
        -------
        Response | None
            A ``429`` HTTP response when the limit is exceeded, or
            ``None`` when the request is allowed to proceed.
        """
        if not self.__rate_limit_enabled:
            return None

        # Skip rate-limiting when the client IP cannot be determined.
        client_ip = adapter.client()
        if not client_ip:
            return None

        allowed = await self.__store.hit(
            client_ip,
            self.__rate_limit_requests,
            self.__rate_limit_window_seconds,
        )

        # If the request exceeds the limit, return a 429 response with a
        # Retry-After header indicating when the client can retry.
        if not allowed:
            return self.__default_responses.error(
                status_code=429,
                description="Too Many Requests",
                expects_json=adapter.wantsJson(),
                headers={
                    "Retry-After": str(self.__rate_limit_window_seconds),
                },
            )

        return None
