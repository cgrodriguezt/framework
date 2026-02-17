import xml.etree.ElementTree as ET
from typing import Any, AsyncGenerator, Iterable
from urllib.parse import parse_qsl
from orionis.http.enums.interfaces import Interface
from orionis.http.estructures.cookies import Cookies
from orionis.http.estructures.headers import Headers
from orionis.http.estructures.query_params import QueryParams
from orionis.http.multipart_stream_parser.form_data import FormData
from orionis.http.multipart_stream_parser.stream_parse import MultipartStreamParser
try:
    import orjson  # type: ignore
    _json_loads = orjson.loads
except ImportError:
    import json
    _json_loads = json.loads

class Request:

    __slots__ = (
        "__scope",
        "__receive_or_protocol",
        "__build_url",
        "__cached_url",
        "__cached_base_url",
        "__build_base_url",
        "__cached_headers",
        "__build_headers",
        "__cached_query_params",
        "__cached_cookies",
        "__cached_ip",
        "__cached_port",
        "__cached_method",
        "__interface",
        "__cached_scheme",
        "__cached_http_version",
        "__body",
        "__cached_json",
        "__cached_form",
        "__stream_consumed",
        "__disconnected",
        "__max_body_size",
        "__parsers",
        "__cached_media_type",
    )

    def __init__(
        self,
        interface: Interface,
        scope: Any,
        receive_or_protocol: Any,
        max_body_size=10 * 1024 * 1024
    ) -> None:
        """
        Initialize HTTPRequest with interface, scope, and protocol/receiver.

        Parameters
        ----------
        interface : Interface
            The interface type (ASGI or RSGI).
        scope : Any
            The request scope object.
        receive_or_protocol : Any
            The receive function or protocol object.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__scope = scope
        self.__receive_or_protocol = receive_or_protocol
        self.__cached_url: str | None = None
        self.__cached_base_url = None
        self.__cached_headers = None
        self.__cached_query_params = None
        self.__cached_cookies = None
        self.__cached_ip = None
        self.__cached_port = None
        self.__cached_method = None
        self.__cached_scheme = None
        self.__cached_http_version = None
        self.__body = None
        self.__cached_json = None
        self.__cached_form = None
        self.__stream_consumed = False
        self.__disconnected = False # NOSONAR
        self.__max_body_size = max_body_size
        self.__cached_media_type = None
        self.__interface = Interface(interface)
        self.__parsers = {
            "application/json": self.json,
            "application/x-www-form-urlencoded": self.urlencoded,
            "multipart/form-data": self.form,
            "application/msgpack": self.msgpack,
            "application/xml": self.xml,
            "text/xml": self.xml,
            "text/html": self.text,
            "text/plain": self.text,
            "application/javascript": self.text,
            "text/javascript": self.text,
            "application/octet-stream": self.binary,
        }
        if Interface(interface) is Interface.RSGI:
            self.__build_url = self.__buildUrlRSGI
            self.__build_base_url = self.__buildBaseUrlRSGI
            self.__build_headers = self.__buildHeadersRSGI
        else:
            self.__build_url = self.__buildUrlASGI
            self.__build_base_url = self.__buildBaseUrlASGI
            self.__build_headers = self.__buildHeadersASGI

    def __buildUrlRSGI(self) -> str:
        """
        Build the full URL from an RSGI scope.

        Returns
        -------
        str
            The constructed request URL.
        """
        scope = self.__scope

        scheme: str = scope.scheme
        host: str = scope.server
        path: str = scope.path
        query: str = scope.query_string

        # Append query string if present
        if query:
            return f"{scheme}://{host}{path}?{query}"
        return f"{scheme}://{host}{path}"

    def __buildUrlASGI(self) -> str: # NOSONAR
        """
        Build the full URL from an ASGI scope.

        Returns
        -------
        str
            The constructed request URL.
        """
        scope = self.__scope

        scheme: str = scope.get("scheme", "http")
        path: str = scope.get("path", "/")
        query_bytes: bytes = scope.get("query_string", b"")
        query: str = query_bytes.decode("latin-1") if query_bytes else ""

        # Preserve duplicate headers (do NOT convert to dict)
        headers: Iterable[tuple[bytes, bytes]] = scope.get("headers", [])

        host: str | None = None

        # Extract host from headers if available
        for key, value in headers:
            if key == b"host":
                host = value.decode("latin-1")
                break

        if host is None:
            server = scope.get("server")
            if server:
                host_name, port = server

                default_port = (
                    80 if scheme in ("http", "ws")
                    else 443
                )

                # Append port only if not default
                if port == default_port:
                    host = host_name
                else:
                    host = f"{host_name}:{port}"
            else:
                # Fallback to path and query only
                return f"{path}?{query}" if query else path

        # Append query string if present
        if query:
            return f"{scheme}://{host}{path}?{query}"
        return f"{scheme}://{host}{path}"

    def __buildBaseUrlRSGI(self) -> str:
        """
        Build and return the base URL from an RSGI scope.

        Returns
        -------
        str
            The base URL composed of scheme and host.
        """
        scheme: str = self.__scope.scheme
        host: str = self.__scope.server

        # Cache the constructed base URL for future use
        return f"{scheme}://{host}"

    def __buildBaseUrlASGI(self) -> str: # NOSONAR
        """
        Build and return the base URL from an ASGI scope.

        Returns
        -------
        str
            The base URL composed of scheme, host, and optional root_path.
        """
        scope: dict[str, Any] = self.__scope

        scheme: str = scope.get("scheme", "http")
        headers: Iterable[tuple[bytes, bytes]] = scope.get("headers", [])
        root_path: str = scope.get("root_path", "")

        host: str | None = None

        # Extract host from headers if present
        for key, value in headers:
            if key == b"host":
                host = value.decode("latin-1")
                break

        if host is None:
            server = scope.get("server")
            if server:
                host_name, port = server
                default_port = 80 if scheme == "http" else 443

                # Append port only if not default
                if port == default_port:
                    host = host_name
                else:
                    host = f"{host_name}:{port}"
            else:
                host = "localhost"

        # Include root_path if present
        if root_path:
            return f"{scheme}://{host}{root_path}"
        else:
            return f"{scheme}://{host}"

    def __buildHeadersASGI(self) -> Headers:
        """
        Build and return ASGI headers as a Headers object.

        Returns
        -------
        Headers
            The headers parsed from the ASGI scope, decoded to strings.
        """
        # Decode header keys and values from bytes to strings
        raw: Iterable[tuple[bytes, bytes]] = self.__scope.get("headers", [])
        decoded: list[tuple[str, str]] = [
            (k.decode("latin-1"), v.decode("latin-1"))
            for k, v in raw
        ]
        return Headers(decoded)

    def __buildHeadersRSGI(self) -> Headers:
        """
        Build and return RSGI headers as a Headers object.

        Returns
        -------
        Headers
            The headers parsed from the RSGI scope, as string pairs.
        """
        # Collect all header key-value pairs from the RSGI scope
        raw: list[tuple[str, str]] = []
        for key in self.__scope.headers:
            values = self.__scope.headers.get_all(key)
            for value in values:
                raw.append((key, value))
        return Headers(raw)

    def __mediaType(self) -> str:
        """
        Return the media type from the Content-Type header.

        Returns
        -------
        str
            The media type in lowercase, without parameters.
        """
        # Extract and normalize the media type from Content-Type header
        if self.__cached_media_type is not None:
            return self.__cached_media_type

        content_type = self.headers.get("content-type", "")
        self.__cached_media_type = content_type.split(";")[0].strip().lower()
        return self.__cached_media_type

    @property
    def url(self) -> str:
        """
        Return the full request URL, using a cached value if available.

        Returns
        -------
        str
            The full request URL.
        """
        if self.__cached_url is None:
            self.__cached_url = self.__build_url()
        return self.__cached_url

    @property
    def base_url(self) -> str:
        """
        Return the base URL for the request.

        Returns
        -------
        str
            The base URL composed of scheme and host.
        """
        # Use cached base URL if available, otherwise build and cache it
        if self.__cached_base_url is None:
            self.__cached_base_url = self.__build_base_url()
        return self.__cached_base_url

    @property
    def headers(self) -> Headers:
        """
        Return the request headers as a Headers object.

        Returns
        -------
        Headers
            The headers associated with the request.
        """
        if self.__cached_headers is None:
            self.__cached_headers = self.__build_headers()
        return self.__cached_headers

    @property
    def query_params(self) -> QueryParams:
        """
        Return parsed query parameters from the request.

        Returns
        -------
        QueryParams
            The parsed query parameters as a QueryParams object.
        """
        # Use cached query parameters if available
        if self.__cached_query_params is not None:
            return self.__cached_query_params

        scope: Any = self.__scope

        # Determine query string based on scope type (RSGI or ASGI)
        if not isinstance(scope, dict):
            query_string: str = scope.query_string or ""
        else:
            query_string_bytes: bytes = scope.get("query_string", b"")
            query_string: str = query_string_bytes.decode("latin-1")

        self.__cached_query_params = QueryParams(query_string)
        return self.__cached_query_params

    @property
    def cookies(self) -> Cookies:
        """
        Return parsed cookies from the request.

        Returns
        -------
        Cookies
            The parsed cookies as a Cookies object.
        """
        # Use cached cookies if available
        if self.__cached_cookies is not None:
            return self.__cached_cookies

        # Retrieve the Cookie header from request headers
        cookie_header: str | None = self.headers.get("cookie")
        self.__cached_cookies = Cookies(cookie_header)
        return self.__cached_cookies

    @property
    def ip(self) -> str | None:
        """
        Return the client's IP address from the request scope.

        Returns
        -------
        str | None
            The client's IP address if available, otherwise None.
        """
        # Use cached IP if available
        if self.__cached_ip is not None:
            return self.__cached_ip

        # Extract the scope for client info retrieval
        scope = self.__scope

        # Extract client info based on scope type (RSGI or ASGI)
        if not isinstance(scope, dict):
            client_raw = scope.client
            if not client_raw:
                return None
            socket_ip, socket_port = client_raw.split(":")
        else:
            client_info = scope.get("client")
            if not client_info:
                return None
            socket_ip, socket_port = client_info

        # Cache the client's IP address and port number for future use
        self.__cached_ip = socket_ip
        self.__cached_port = socket_port

        # Return the cached IP address (which may be None if not available)
        return self.__cached_ip

    @property
    def port(self) -> int | None:
        """
        Return the client's port number from the request scope.

        Returns
        -------
        int | None
            The client's port number if available, otherwise None.
        """
        # Use cached port if available
        if self.__cached_port is not None:
            return self.__cached_port

        # Extract the scope for client info retrieval
        scope = self.__scope

        # Extract client (RSGI or ASGI)
        if self.__interface is Interface.RSGI:
            client_info = scope.client.split(":")
        else:
            client_info = scope.get("client")

        # Extract and cache the client's port number
        socket_ip, socket_port = client_info
        self.__cached_ip = socket_ip
        self.__cached_port = socket_port

        # Return the cached port number (which may be None if not available)
        return self.__cached_port

    @property
    def method(self) -> str:
        """
        Return the HTTP request method.

        Returns
        -------
        str
            The HTTP method of the request, such as 'GET' or 'POST'.
        """
        # Return cached method if available
        if self.__cached_method is not None:
            return self.__cached_method

        # Extract the scope for method retrieval
        scope = self.__scope

        # Determine method based on interface type
        if self.__interface is Interface.RSGI:
            method = scope.method
        else:
            method = scope.get("method", "GET")
        self.__cached_method = method.upper()

        # Return the cached method (which may be None if not available)
        return self.__cached_method

    @property
    def scheme(self) -> str:
        """
        Return the URL scheme (e.g., 'http' or 'https') of the request.

        Returns
        -------
        str
            The URL scheme of the request.
        """
        # Return cached scheme if available
        if self.__cached_scheme is not None:
            return self.__cached_scheme

        # Extract the scope for scheme retrieval
        scope = self.__scope

        # Determine scheme based on interface type
        if self.__interface is Interface.RSGI:
            scheme = scope.scheme
        else:
            scheme = scope.get("scheme", "http")
        self.__cached_scheme = scheme.lower()

        # Return the cached scheme (which may be None if not available)
        return self.__cached_scheme

    @property
    def interface(self) -> Interface:
        """
        Return the interface type of the request (ASGI or RSGI).

        Returns
        -------
        Interface
            The interface type of the request.
        """
        return self.__interface

    @property
    def api_key(self) -> str | None:
        """
        Return the API key from the request headers if present.

        Returns
        -------
        str | None
            The API key from the 'X-API-Key' header, or None if not present.
        """
        return self.headers.get("X-API-Key")

    @property
    def authorization(self) -> str | None:
        """
        Return the Authorization header value if present.

        Returns
        -------
        str | None
            The value of the 'Authorization' header, or None if not present.
        """
        return self.headers.get("Authorization")

    @property
    def http_version(self) -> str:
        """
        Return the HTTP version of the request.

        Returns
        -------
        str
            The HTTP version string, such as '1.1' or '2'.
        """
        # Return cached HTTP version if available
        if self.__cached_http_version is not None:
            return self.__cached_http_version
        scope: Any = self.__scope

        # Determine HTTP version based on interface type
        if self.__interface is Interface.RSGI:
            http_version: str = scope.http_version
        else:
            http_version: str = scope.get("http_version", "1.1")
        self.__cached_http_version = http_version

        # Return the cached HTTP version (which may be None if not available)
        return self.__cached_http_version

    def hasApiKey(self) -> bool:
        """
        Check if the request contains an API key in the headers.

        Returns
        -------
        bool
            True if the 'X-API-Key' header is present, False otherwise.
        """
        return "X-API-Key" in self.headers

    def bearerToken(self, remove_prefix: str = "Bearer ") -> str | None:
        """
        Retrieve the token from the Authorization header.

        Parameters
        ----------
        remove_prefix : str, optional
            Prefix to remove from the token. Defaults to "Bearer ".

        Returns
        -------
        str | None
            The token from the Authorization header with the prefix removed,
            or None if not present.
        """
        # Get the Authorization header and remove the prefix if present
        auth_header: str | None = self.headers.get("Authorization")
        if auth_header and auth_header.startswith(remove_prefix):
            return auth_header[len(remove_prefix):]
        return auth_header

    def hasBearerToken(self) -> bool:
        """
        Check if the Authorization header contains a bearer token.

        Returns
        -------
        bool
            True if the Authorization header contains a token with the
            'Bearer ' prefix, otherwise False.
        """
        # Retrieve the Authorization header and check for 'Bearer ' prefix
        auth_header: str | None = self.headers.get("Authorization")
        return auth_header is not None and auth_header.startswith("Bearer ")

    async def stream(self) -> AsyncGenerator[bytes, None]: # NOSONAR
        """
        Yield chunks of the request body as they arrive.

        Streaming-first body reader. Optimized for RSGI (Granian returns raw bytes).

        Returns
        -------
        AsyncGenerator[bytes, None]
            Yields chunks of the request body as bytes.
        """
        # Yield cached body if available
        if self.__body is not None:
            yield self.__body
            return

        # Prevent multiple consumption of the stream
        if self.__stream_consumed:
            error_msg = "Request stream already consumed"
            raise RuntimeError(error_msg)

        self.__stream_consumed = True
        total = 0

        # Handle RSGI (Granian) streaming
        if self.__interface is Interface.RSGI:
            async for chunk in self.__receive_or_protocol:
                if not chunk:
                    continue

                total += len(chunk)
                if total > self.__max_body_size:
                    raise ValueError("Request body too large")

                yield chunk

            return

        # Handle ASGI streaming fallback
        while True:
            message = await self.__receive_or_protocol()

            # Detect client disconnect
            if message["type"] == "http.disconnect":
                self.__disconnected = True
                error_msg = "Client disconnected"
                raise RuntimeError(error_msg)

            chunk = message.get("body", b"")

            if chunk:
                total += len(chunk)
                if total > self.__max_body_size:
                    error_msg = "Request body too large"
                    raise ValueError(error_msg)

                yield chunk

            # End of body stream
            if not message.get("more_body", False):
                break

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
        # Return cached body if available
        if self.__body is not None:
            return self.__body

        # Raise error if stream already consumed and body not cached
        if self.__stream_consumed and self.__body is None:
            error_msg = "Request stream already consumed"
            raise RuntimeError(error_msg)

        # Buffer chunks efficiently using bytearray
        buffer = bytearray()

        async for chunk in self.stream():
            buffer.extend(chunk)

        self.__body = bytes(buffer)
        return self.__body

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
        # Return cached JSON if available
        if self.__cached_json is not None:
            return self.__cached_json

        content_type = self.headers.get("content-type", "")

        # Validate Content-Type header for JSON
        if not (content_type == "application/json" or content_type.endswith("+json")):
            error_msg = "Content-Type must be application/json"
            raise ValueError(error_msg)

        raw = await self.body()

        # Raise error if body is empty
        if not raw:
            error_msg = "Empty JSON body"
            raise ValueError(error_msg)

        # Attempt to parse JSON and cache the result
        try:
            self.__cached_json = _json_loads(raw)
        except Exception as exc:
            raise ValueError("Invalid JSON payload") from exc

        # Return the cached JSON object (which may be None if parsing failed)
        return self.__cached_json

    async def data(self) -> Any:
        """
        Parse and return structured request data based on Content-Type.

        Returns
        -------
        Any
            Structured data parsed from the request body, or raw bytes if no
            parser is available.
        """
        # Determine the media type from the Content-Type header
        media_type = self.__mediaType()

        # If no media type, return the raw body
        if not media_type:
            return await self.body()

        # Look up the parser for the media type
        parser = self.__parsers.get(media_type)

        # If no parser found, return the raw body
        if not parser:
            return await self.body()

        # Call the appropriate parser method
        return await parser()

    async def urlencoded(self) -> dict[str, Any]:
        """
        Parse the request body as URL-encoded form data.

        Returns
        -------
        dict[str, Any]
            The parsed form data as a dictionary.
        """
        # Return cached form data if available
        if self.__cached_form is not None:
            return self.__cached_form

        # Decode the raw request body to text
        raw = await self.body()
        text = raw.decode("utf-8")

        # Parse the URL-encoded form data
        self.__cached_form = dict(parse_qsl(text, keep_blank_values=True))
        return self.__cached_form

    async def binary(self) -> bytes:
        """
        Parse the request body as binary data.

        Returns
        -------
        bytes
            The raw request body as bytes.
        """
        # Return the raw request body as bytes
        return await self.body()

    async def text(self) -> str:
        """
        Decode the request body as UTF-8 text.

        Returns
        -------
        str
            The decoded request body as a string.
        """
        # Decode the raw request body to a UTF-8 string
        raw = await self.body()
        return raw.decode("utf-8")

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
        # Get the raw request body as bytes
        raw = await self.body()

        # Parse and return the root XML element
        return ET.fromstring(raw)

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
        try:
            import msgpack # type: ignore
        except ImportError:
            error_msg = "msgpack support not installed"
            raise RuntimeError(error_msg)

        # Get the raw request body as bytes
        raw = await self.body()
        return msgpack.loads(raw)

    async def form(self) -> FormData:
        """
        Parse and return multipart form data.
        """

        content_type = self.headers.get("content-type", "")

        if "multipart/form-data" not in content_type:
            raise ValueError("Not multipart/form-data")

        try:
            boundary = content_type.split("boundary=")[1].encode()
        except IndexError:
            raise ValueError("Missing multipart boundary")

        parser = MultipartStreamParser(
            self.stream(),
            boundary,
        )

        return await parser.parse()