from __future__ import annotations
from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from orionis.http.enums.interfaces import Interface
    from orionis.http.estructures.cookies import Cookies
    from orionis.http.estructures.headers import Headers
    from orionis.http.estructures.query_params import QueryParams
    from orionis.http.payload.form_data import FormData

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
    def baseUrl(self) -> str:
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
    def queryParams(self) -> QueryParams:
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
    def path(self) -> str:
        """
        Return the request path.

        Returns
        -------
        str
            The path component of the request URL.
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
    def httpVersion(self) -> str:
        """
        Return the HTTP version of the request.

        Returns
        -------
        str
            The HTTP version string, such as '1.1' or '2'.
        """

    @property
    @abstractmethod
    def userAgent(self) -> str | None:
        """
        Return the User-Agent string from the request headers.

        Returns
        -------
        str | None
            The User-Agent string if present, otherwise None.
        """

    # ---- Authentication By X-API-Key Helpers ----

    @property
    @abstractmethod
    def apiKey(self) -> str | None:
        """
        Return the API key from the request headers if present.

        Returns
        -------
        str | None
            The API key from the 'X-API-Key' header, or None if not present.
        """

    # ---- Authentication By Bearer Token Helpers ----

    @property
    @abstractmethod
    def bearerToken(self) -> str | None:
        """
        Return the bearer token from the Authorization header if present.

        Returns
        -------
        str | None
            The bearer token extracted from the 'Authorization' header,
            or None if not present or does not start with 'Bearer '.
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

    # ---- Content Negotiation Helpers ----

    @abstractmethod
    def wantsJson(self) -> bool:
        """
        Determine if the client prefers a JSON response based on the Accept header.

        Returns
        -------
        bool
            True if the Accept header indicates JSON is preferred, otherwise False.
        """

    @abstractmethod
    def accepts(self, mime: str) -> bool:
        """
        Check if the client accepts a specific MIME type.

        Parameters
        ----------
        mime : str
            The MIME type to check.

        Returns
        -------
        bool
            True if the MIME type is present in the Accept header.
        """

    @abstractmethod
    def isAjax(self) -> bool:
        """
        Determine if the request was made via AJAX.

        Returns
        -------
        bool
            True if the X-Requested-With header is 'XMLHttpRequest'.
        """

    @abstractmethod
    def expectsHtml(self) -> bool:
        """
        Determine if the client expects an HTML response based on the Accept header.

        Returns
        -------
        bool
            True if the Accept header indicates HTML is expected.
        """

    @abstractmethod
    def wantsXml(self) -> bool:
        """
        Determine if the client prefers an XML response based on the Accept header.

        Returns
        -------
        bool
            True if the Accept header indicates XML is preferred.
        """
    # ---- Body Parsing Methods ----

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
    async def json(self) -> object:
        """
        Parse and return the request body as JSON.

        Validates the Content-Type header and parses the request body as JSON.
        Uses a cached result if available.

        Returns
        -------
        object
            The parsed JSON value (dict, list, str, int, float, bool, or None).

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
        xml.etree.ElementTree.ParseError
            If the XML body is malformed or contains forbidden constructs.
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
        UnsupportedMediaTypeException
            If the Content-Type is not multipart/form-data.
        ValueError
            If the multipart boundary is missing.
        """

    @property
    @abstractmethod
    def state(self) -> SimpleNamespace:
        """
        Return the mutable per-request state namespace.

        Middleware and handlers can attach arbitrary attributes to this
        namespace without polluting the scope dict.

        Returns
        -------
        types.SimpleNamespace
            The mutable state object for this request.
        """

    @property
    @abstractmethod
    def scope(self) -> dict[str, Any]:
        """
        Return the raw ASGI / RSGI connection scope.

        Exposes the underlying scope dict so that ASGI-aware middleware,
        tracing libraries, and extensions can read or annotate transport-level
        data without requiring framework-specific adapters.

        Returns
        -------
        dict[str, Any]
            The raw scope dictionary provided by the transport layer.
        """

    @abstractmethod
    def param(self, key: str | None = None) -> dict[str, Any] | str | None:
        """
        Return all path parameters or a specific one by key.

        Parameters
        ----------
        key : str | None, optional
            The specific path parameter key to retrieve. If None, returns all
            path parameters as a dict. Defaults to None.

        Returns
        -------
        dict[str, Any] | str | None
            All path parameters if key is None, the specific parameter value
            if key exists, or None if key is not found.
        """
