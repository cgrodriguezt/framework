from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.foundation.config.http.entitites.security import HTTPSecurity

if TYPE_CHECKING:
    from orionis.http.adapters.request.contracts.transport import TransportAdapter
    from orionis.http.default.contracts.responses import IDefaultResponses
    from orionis.http.response import Response

class SecurityMiddleware:

    # ruff: noqa: C901

    def __init__(
        self,
        config: dict,
        default_responses: IDefaultResponses,
    ) -> None:
        """Initialize the middleware with the given security configuration.

        Parameters
        ----------
        config : dict
            A dictionary whose keys must match ``HTTPSecurity`` fields.
        default_responses : IDefaultResponses
            Predefined default responses for common HTTP errors.

        Returns
        -------
        None
        """
        # Parse and store the security configuration
        self.__config = HTTPSecurity(**config)
        self.__validate_headers = self.__config.validate_headers
        self.__max_header_size = self.__config.max_header_size
        self.__block_multiple_host_headers = (
            self.__config.block_multiple_host_headers
        )

        # Pre-build a lowercase set for O(1) membership tests.
        self.__allowed_hosts: set[str] = set()
        if isinstance(self.__config.allowed_hosts, list):
            self.__allowed_hosts = {
                h.lower() for h in self.__config.allowed_hosts
            }

        # Store the default responses for use in the handler.
        self.__default_responses = default_responses

    def handle( # NOSONAR
        self,
        adapter: TransportAdapter,
    ) -> Response | None:
        """Inspect the incoming request and enforce all security policies.

        Runs four sequential checks in order: per-header size cap,
        CRLF-injection detection, duplicate Host header guard, and
        host allowlist validation.  Returns a ``Response`` on the
        first violation, or ``None`` when all checks pass.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport abstraction providing header access and
            client-preference detection.

        Returns
        -------
        Response | None
            An HTTP error response when a check fails, or ``None``
            when the request is considered safe to proceed.
        """
        # Detect JSON preference once; reused by every early-return branch.
        wants_json = adapter.wantsJson()

        # 1. Reject headers that exceed the configured byte cap (HTTP 431).
        if self.__max_header_size:
            for name, value in adapter.headers().byteItems():
                if len(name) + len(value) > self.__max_header_size:
                    return self.__default_responses.error(
                        status_code=431,
                        description="Header too large.",
                        expects_json=wants_json,
                    )

        # 2. Reject headers that contain bare CR or LF (CRLF injection).
        if self.__validate_headers:
            for name, value in adapter.headers().items():
                if (
                    "\r" in name or "\n" in name
                    or "\r" in value or "\n" in value
                ):
                    return self.__default_responses.error(
                        status_code=400,
                        description="Invalid header format.",
                        expects_json=wants_json,
                    )

        # 3. Reject requests that carry more than one Host header.
        if self.__block_multiple_host_headers:
            host_values = adapter.headers().getAll("host")
            if host_values and len(host_values) > 1:
                return self.__default_responses.error(
                    status_code=400,
                    description="Multiple Host headers not allowed.",
                    expects_json=wants_json,
                )

        # 4. Validate Host against the allowlist (strip port, lowercase).
        if self.__allowed_hosts:
            raw_host = adapter.headers().get("host")
            if not raw_host:
                return self.__default_responses.error(
                    status_code=400,
                    description="Host header not allowed.",
                    expects_json=wants_json,
                )
            # Strip the optional port component before the lookup.
            host = raw_host.lower().split(":")[0]
            if host not in self.__allowed_hosts:
                return self.__default_responses.error(
                    status_code=400,
                    description="Host header not allowed.",
                    expects_json=wants_json,
                )

        # All checks passed; allow the request to proceed.
        return None
