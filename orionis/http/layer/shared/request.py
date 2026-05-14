from __future__ import annotations
from typing import TYPE_CHECKING, Final
from orionis.foundation.config.http.entitites.request import HTTPRequest

if TYPE_CHECKING:
    from orionis.http.adapters.request.contracts.transport import TransportAdapter
    from orionis.http.default.contracts.responses import IDefaultResponses
    from orionis.http.response import Response

class RequestMiddleware:

    ALLOWED_METHODS: Final[frozenset[str]] = frozenset(
        {
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        },
    )

    def __init__(
        self,
        config: dict,
        default_responses: IDefaultResponses,
    ) -> None:
        """Initialize the middleware with the given request configuration.

        Parameters
        ----------
        config : dict
            Raw configuration mapping forwarded to ``HTTPRequest``.
        default_responses : IDefaultResponses
            Predefined default responses for common HTTP errors.

        Returns
        -------
        None
            Instance attributes are set in-place.
        """
        # Parse and store the request configuration
        request_config = HTTPRequest(**config)

        # Build a lowercase set of permitted MIME types, or wildcard "*"
        self.__allowed_content_types = (
            {
                item.lower()
                for item in request_config.allowed_content_types
            }
            if isinstance(request_config.allowed_content_types, list)
            else "*"
        )

        self.__max_content_length = request_config.max_content_length

        self.__enable_method_override = (
            request_config.enable_method_override
        )

        # Normalise the override header name to lowercase for lookup
        self.__method_override_header = (
            request_config.method_override_header
            .strip()
            .lower()
        )

        # Store the default responses for later use in validation checks.
        self.__default_responses = default_responses

    def __isAllowedContentType(
        self,
        content_type: str,
    ) -> bool:
        """Check whether the given content type is permitted.

        Parameters
        ----------
        content_type : str
            Lowercase MIME type extracted from the ``Content-Type``
            header (parameters already stripped).

        Returns
        -------
        bool
            ``True`` if the content type is in the allowlist or the
            wildcard ``"*"`` is active; ``False`` otherwise.
        """
        # Wildcard means every content type is accepted
        if self.__allowed_content_types == "*":
            return True

        return content_type in self.__allowed_content_types

    def __isValidContentLength(
        self,
        content_length: int,
    ) -> bool:
        """Check whether the given content length is within the limit.

        Parameters
        ----------
        content_length : int
            Parsed value of the ``Content-Length`` header in bytes.

        Returns
        -------
        bool
            ``True`` if the length is within the configured maximum or
            no limit is set; ``False`` if the limit is exceeded.
        """
        if (
            isinstance(self.__max_content_length, int)
            and self.__max_content_length > 0
        ):
            return content_length <= self.__max_content_length

        return True

    def getMaxContentLength(self) -> int | None:
        """
        Return the configured maximum content length in bytes.

        Returns
        -------
        int | None
            The maximum content length in bytes, or None if no limit is set.
        """
        return self.__max_content_length

    def handle(
        self,
        adapter: TransportAdapter,
    ) -> Response | None:
        """Validate and normalise the incoming HTTP request.

        Checks the content-type allowlist, the content-length limit,
        and optionally overrides the HTTP method via a request header.

        Parameters
        ----------
        adapter : TransportAdapter
            Transport adapter exposing the normalised request data.
            Headers must already be lowercased by the adapter.

        Returns
        -------
        Response | None
            An error ``Response`` (415 or 413) when validation fails,
            or ``None`` when the request passes all checks.
        """
        # Detect JSON preference once; reused by every early-return branch.
        wants_json = adapter.wantsJson()

        # Headers are already normalised to lowercase by the adapter
        headers = adapter.headers()

        # Validate Content-Type
        if self.__allowed_content_types != "*":
            content_type = (
                headers.get("content-type", "")
                .split(";")[0]
                .strip()
                .lower()
            )
            if not self.__isAllowedContentType(content_type):
                return self.__default_responses.error(
                    status_code=415,
                    description=f"Unsupported Media Type: {content_type}",
                    expects_json=wants_json,
                )

        # Validate Content-Length
        content_length = headers.get("content-length")

        if (
            isinstance(content_length, str)
            and content_length.isdigit()
        ):
            parsed_content_length = int(content_length)

            if not self.__isValidContentLength(parsed_content_length):
                return self.__default_responses.error(
                    status_code=413,
                    description=(
                        f"Payload Too Large: "
                        f"{parsed_content_length} bytes"
                    ),
                    expects_json=wants_json,
                )

        # HTTP Method Override
        if self.__enable_method_override:
            override_method = headers.get(self.__method_override_header)
            if isinstance(override_method, str):
                override_method = override_method.strip().upper()
                if override_method in self.ALLOWED_METHODS:
                    adapter.setMethod(override_method)

        # All checks passed; allow the request to proceed.
        return None
