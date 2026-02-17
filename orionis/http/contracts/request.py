from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from collections.abc import AsyncGenerator
    from orionis.http.enums.interfaces import Interface
    from orionis.http.estructures.cookies import Cookies
    from orionis.http.estructures.headers import Headers
    from orionis.http.estructures.query_params import QueryParams
    from orionis.http.multipart.form_data import FormData

class IRequest(ABC):

    # ruff: noqa: ANN401

    @property
    @abstractmethod
    def url(self) -> str:
        """
        Return the full request URL, using a cached value if available.

        Returns
        -------
        str
            The full request URL.
        """

    @property
    @abstractmethod
    def base_url(self) -> str:
        """
        Return the base URL for the request.

        Returns
        -------
        str
            The base URL composed of scheme and host.
        """

    @property
    @abstractmethod
    def headers(self) -> Headers:
        """
        Return the request headers as a Headers object.

        Returns
        -------
        Headers
            The headers associated with the request.
        """

    @property
    @abstractmethod
    def query_params(self) -> QueryParams:
        """
        Return parsed query parameters from the request.

        Returns
        -------
        QueryParams
            The parsed query parameters as a QueryParams object.
        """

    @property
    @abstractmethod
    def cookies(self) -> Cookies:
        """
        Return parsed cookies from the request.

        Returns
        -------
        Cookies
            The parsed cookies as a Cookies object.
        """

    @property
    @abstractmethod
    def ip(self) -> str | None:
        """
        Return the client's IP address from the request scope.

        Returns
        -------
        str | None
            The client's IP address if available, otherwise None.
        """

    @property
    @abstractmethod
    def port(self) -> int | None:
        """
        Return the client's port number from the request scope.

        Returns
        -------
        int | None
            The client's port number if available, otherwise None.
        """

    @property
    @abstractmethod
    def method(self) -> str:
        """
        Return the HTTP request method.

        Returns
        -------
        str
            The HTTP method of the request, such as 'GET' or 'POST'.
        """

    @property
    @abstractmethod
    def scheme(self) -> str:
        """
        Return the URL scheme (e.g., 'http' or 'https') of the request.

        Returns
        -------
        str
            The URL scheme of the request.
        """

    @property
    @abstractmethod
    def interface(self) -> Interface:
        """
        Return the interface type of the request (ASGI or RSGI).

        Returns
        -------
        Interface
            The interface type of the request.
        """

    @property
    @abstractmethod
    def api_key(self) -> str | None:
        """
        Return the API key from the request headers if present.

        Returns
        -------
        str | None
            The API key from the 'X-API-Key' header, or None if not present.
        """

    @property
    @abstractmethod
    def authorization(self) -> str | None:
        """
        Return the Authorization header value if present.

        Returns
        -------
        str | None
            The value of the 'Authorization' header, or None if not present.
        """

    @property
    @abstractmethod
    def http_version(self) -> str:
        """
        Return the HTTP version of the request.

        Returns
        -------
        str
            The HTTP version string, such as '1.1' or '2'.
        """

    @abstractmethod
    def hasApiKey(self) -> bool:
        """
        Check if the request contains an API key in the headers.

        Returns
        -------
        bool
            True if the 'X-API-Key' header is present, False otherwise.
        """

    @abstractmethod
    def bearerToken(self, remove_prefix: str = "Bearer ") -> str | None:
        """
        Retrieve the token from the Authorization header.

        Parameters
        ----------
        remove_prefix : str, optional
            @abstractmethodPrefix to remove from the token
            . Defaults to "Bearer ".

        Returns
        -------
        str | None
            The token from the Authorization header with the prefix removed,
            or None if not present.
        """

    @abstractmethod
    def hasBearerToken(self) -> bool:
        """
        Check if the Authorization header contains a bearer token.

        Returns
        -------
        bool
            True if the Authorization header contains a token with the
            'Bearer ' prefix, otherwise False.
        """

    @abstractmethod
    async def stream(self) -> AsyncGenerator[bytes, None]: # NOSONAR
        """
        Yield chunks of the request body as they arrive.

        Streaming-first body reader. Optimized for RSGI (Granian returns raw bytes).

        Returns
        -------
        AsyncGenerator[bytes, None]
            Yields chunks of the request body as bytes.
        """

    @abstractmethod
    async def body(self) -> bytes:
        """
        Return the full request body as bytes.

        Buffer the stream on first call and cache the result. Raise an error if the
        stream was already consumed elsewhere.

        Parameters
        ----------
        None

        Returns
        -------
        bytes
            The complete request body as bytes.
        """

    @abstractmethod
    async def json(self) -> dict[str, Any]:
        """
        Parse and return the request body as JSON.

        Validates the Content-Type header and parses the request body as JSON.
        Uses a cached result if available.

        Returns
        -------
        dict[str, Any]
            The parsed JSON object.

        Raises
        ------
        ValueError
            If the Content-Type is not application/json, the body is empty,
            or the payload is invalid JSON.
        """

    @abstractmethod
    async def data(self) -> Any:
        """
        Parse and return structured request data based on Content-Type.

        Returns
        -------
        Any
            Structured data parsed from the request body, or raw bytes if no
            parser is available.
        """

    @abstractmethod
    async def urlencoded(self) -> dict[str, Any]:
        """
        Parse the request body as URL-encoded form data.

        Returns
        -------
        dict[str, Any]
            The parsed form data as a dictionary.
        """

    @abstractmethod
    async def binary(self) -> bytes:
        """
        Parse the request body as binary data.

        Returns
        -------
        bytes
            The raw request body as bytes.
        """

    @abstractmethod
    async def text(self) -> str:
        """
        Decode the request body as UTF-8 text.

        Returns
        -------
        str
            The decoded request body as a string.
        """

    @abstractmethod
    async def xml(self) -> ET.Element:
        """
        Parse the request body as XML and return the root element.

        Returns
        -------
        ET.Element
            The root element parsed from the XML request body.

        Raises
        ------
        ET.ParseError
            If the XML body is invalid.
        """

    @abstractmethod
    async def msgpack(self) -> dict[str, Any]:
        """
        Parse and return the request body as MessagePack.

        Returns
        -------
        dict[str, Any]
            The parsed MessagePack object from the request body.

        Raises
        ------
        RuntimeError
            If msgpack support is not installed.
        """

    @abstractmethod
    async def form(self) -> FormData:
        """
        Parse and return multipart form data.

        Returns
        -------
        FormData
            The parsed multipart form data.

        Raises
        ------
        ValueError
            If the request is not multipart/form-data or the boundary is missing.
        """
