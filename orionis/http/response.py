from __future__ import annotations
import asyncio
import json
import mimetypes
from collections.abc import AsyncIterable as AsyncIterableABC
from datetime import date, datetime, time, timezone
from decimal import Decimal
from email.utils import format_datetime
from enum import Enum
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any, AsyncIterable, Iterable, Literal, Mapping, MutableMapping
from uuid import UUID
from orionis.http.contracts.response import IResponse
from orionis.http.status import HTTPStatus
from orionis.support.background.task import BackgroundTask
try:
    import orjson # pyright: ignore[reportMissingImports]
except ImportError:
    orjson = None

class Response(IResponse):

    def __init__(
        self,
        content: Any = None,
        status_code: HTTPStatus | int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Initialize the BaseResponse object.

        Parameters
        ----------
        content : Any, optional
            The response content or stream.
        status_code : HTTPStatus | int, optional
            The HTTP status code for the response.
        headers : Mapping[str, str] | None, optional
            The headers to include in the response.
        media_type : str | None, optional
            The media type of the response.
        background : BackgroundTask | None, optional
            The background task to run after response.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Validate status_code type and range
        if not isinstance(status_code, int):
            error_msg = "status_code must be an integer"
            raise TypeError(error_msg)

        if not 100 <= status_code <= 599:
            error_msg = "status_code must be between 100 and 599"
            raise ValueError(error_msg)

        self.status_code = status_code
        self.media_type = media_type
        self.charset = "utf-8"

        # Handle body or stream content
        self._original_content = content
        self._body: bytes | None = None
        self._stream: AsyncIterable[bytes] | None = None

        if isinstance(content, AsyncIterableABC):
            self._stream = content
        else:
            self._body = self.render(content)

        # Initialize headers
        self._headers: MutableMapping[str, list[str]] = {}

        if headers:
            if not isinstance(headers, Mapping):
                error_msg = "headers must be a mapping"
                raise TypeError(error_msg)

            for key, value in headers.items():
                self.addHeader(key, value)

        # Validate background task type
        if background is not None and not isinstance(background, BackgroundTask):
            error_msg = "background must be a BackgroundTask or None"
            raise TypeError(error_msg)

        self.background = background

    def render(self, content: Any) -> bytes:
        """
        Render the content to bytes.

        Parameters
        ----------
        content : Any
            The content to render.

        Returns
        -------
        bytes
            The rendered content as bytes.
        """
        if content is None:
            return b""

        if isinstance(content, (bytes, bytearray, memoryview)):
            return bytes(content)

        if isinstance(content, str):
            return content.encode(self.charset)

        return str(content).encode(self.charset)

    def addHeader(self, key: str, value: str) -> None:
        """
        Add a header to the response.

        Parameters
        ----------
        key : str
            The header name.
        value : str
            The header value.

        Returns
        -------
        None
            This method does not return a value.
        """
        key_lower = key.lower()
        # Add the header value to the list for the given header key
        self._headers.setdefault(key_lower, []).append(value)

    def setHeader(self, key: str, value: str) -> None:
        """
        Set a header, replacing any existing values.

        Parameters
        ----------
        key : str
            The header name.
        value : str
            The header value.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Replace any existing values for the header key
        self._headers[key.lower()] = [value]

    def getHeader(self, key: str) -> list[str] | None:
        """
        Get the values for a header.

        Parameters
        ----------
        key : str
            The header name.

        Returns
        -------
        list[str] | None
            The list of header values, or None if not present.
        """
        return self._headers.get(key.lower())

    def hasHeader(self, key: str) -> bool:
        """
        Check if a header is present.

        Parameters
        ----------
        key : str
            The header name.

        Returns
        -------
        bool
            True if the header is present, False otherwise.
        """
        return key.lower() in self._headers

    def removeHeader(self, key: str) -> None:
        """
        Remove a header from the response.

        Parameters
        ----------
        key : str
            The header name.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove the header if it exists
        self._headers.pop(key.lower(), None)

    def getRawHeaders(self) -> list[tuple[bytes, bytes]]:
        """
        Return the headers as a list of (key, value) byte tuples.

        Returns
        -------
        list of tuple of (bytes, bytes)
            The headers as (key, value) pairs encoded in latin-1.
        """
        raw: list[tuple[bytes, bytes]] = []
        # Encode header keys and values as bytes for raw output
        for key, values in self._headers.items():
            for value in values:
                raw.append(
                    (key.encode("latin-1"), value.encode("latin-1"))
                )
        return raw

    def setCookie( # NOSONAR
        self,
        key: str,
        value: str = "",
        *,
        max_age: int | None = None,
        expires: datetime | str | int | None = None,
        path: str | None = "/",
        domain: str | None = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Literal["lax", "strict", "none"] | None = "lax",
        partitioned: bool = False,
    ) -> None:
        """
        Set a cookie header in the response.

        Parameters
        ----------
        key : str
            The cookie name.
        value : str, optional
            The cookie value. Defaults to an empty string.
        max_age : int | None, optional
            The maximum age of the cookie in seconds.
        expires : datetime | str | int | None, optional
            The expiration date of the cookie.
        path : str | None, optional
            The path for which the cookie is valid.
        domain : str | None, optional
            The domain for which the cookie is valid.
        secure : bool, optional
            Whether the cookie is secure.
        http_only : bool, optional
            Whether the cookie is HTTP only.
        same_site : str | None, optional
            The SameSite policy for the cookie.
        partitioned : bool, optional
            Whether the cookie is partitioned.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Create a SimpleCookie and set the key-value pair
        cookie = SimpleCookie()
        cookie[key] = value
        morsel = cookie[key]

        # Set max-age if provided
        if max_age is not None:
            morsel["max-age"] = str(max_age)

        # Format expires if it's a datetime
        if isinstance(expires, datetime):
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            expires = format_datetime(
                expires.astimezone(timezone.utc),
                usegmt=True,
            )

        # Set expires if provided
        if expires is not None:
            morsel["expires"] = str(expires)

        # Set path if provided
        if path:
            morsel["path"] = path

        # Set domain if provided
        if domain:
            morsel["domain"] = domain

        # Set SameSite policy if provided
        if same_site is not None:
            s = same_site.lower()
            if s not in {"lax", "strict", "none"}:
                error_msg = (
                    "same_site must be 'lax', 'strict' or 'none'"
                )
                raise ValueError(error_msg)
            if s == "none" and not secure:
                error_msg = "SameSite=None requires secure=True"
                raise ValueError(error_msg)
            morsel["samesite"] = s

        # Set secure flag if True
        if secure:
            morsel["secure"] = True

        # Set HttpOnly flag if True
        if http_only:
            morsel["httponly"] = True

        # Set partitioned flag if True
        if partitioned:
            morsel["partitioned"] = True

        # Add the Set-Cookie header to the response
        cookie_value = cookie.output(header="").strip()
        self.addHeader("set-cookie", cookie_value)

    def deleteCookie(
        self,
        key: str,
        *,
        path: str = "/",
        domain: str | None = None,
    ) -> None:
        """
        Delete a cookie by setting its expiration to the past.

        Parameters
        ----------
        key : str
            The name of the cookie to delete.
        path : str, default="/"
            The path for which the cookie is valid.
        domain : str | None, optional
            The domain for which the cookie is valid.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set the cookie with max_age and expires to remove it from the client
        self.setCookie(
            key,
            max_age=0,
            expires=datetime(1970, 1, 1, tzinfo=timezone.utc),
            path=path,
            domain=domain,
        )

    def getBody(self) -> bytes | None:
        """
        Return the response body as bytes.

        Returns
        -------
        bytes | None
            The response body as bytes, or None if not set.
        """
        return self._body

    def getStream(self) -> AsyncIterable[bytes] | None:
        """
        Return the response stream if present.

        Returns
        -------
        AsyncIterable[bytes] | None
            The response stream, or None if not set.
        """
        return self._stream

    def hasStream(self) -> bool:
        """
        Check if the response has a stream.

        Returns
        -------
        bool
            True if a stream is present, False otherwise.
        """
        return self._stream is not None

    async def runBackground(self) -> None:
        """
        Run the background task if it exists.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Await the background task if it is set
        if self.background:
            await self.background()

class HTMLResponse(Response):

    def __init__(
        self,
        content: str | bytes = "",
        status_code: HTTPStatus | int = 200,
        headers: Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Initialize an HTMLResponse with HTML content.

        Parameters
        ----------
        content : str | bytes, optional
            HTML content to include in the response.
        status_code : HTTPStatus | int, optional
            HTTP status code for the response.
        headers : Mapping[str, str] | None, optional
            Optional response headers.
        background : BackgroundTask | None, optional
            Optional background task to run after response.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Initialize the parent Response with HTML media type
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="text/html",
            background=background,
        )

        # Ensure the Content-Type header is set for HTML responses
        if not self.hasHeader("content-type"):
            content_type = f"text/html; charset={self.charset}"
            self.setHeader("content-type", content_type)

class PlainTextResponse(Response):

    def __init__(
        self,
        content: str | bytes = "",
        status_code: HTTPStatus | int = 200,
        headers: Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Initialize a plain text response.

        Parameters
        ----------
        content : str | bytes, optional
            The plain text content for the response.
        status_code : HTTPStatus | int, optional
            The HTTP status code for the response.
        headers : Mapping[str, str] | None, optional
            Optional response headers.
        background : BackgroundTask | None, optional
            Optional background task to run after response.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Initialize the parent Response with plain text media type
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="text/plain",
            background=background,
        )

        # Ensure the Content-Type header is set for plain text responses
        if not self.hasHeader("content-type"):
            content_type = f"text/plain; charset={self.charset}"
            self.setHeader("content-type", content_type)

class JSONResponse(Response):

    def __init__(
        self,
        content: Any,
        status_code: HTTPStatus | int = 200,
        headers: Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
        *,
        indent: int | None = None,
        ensure_ascii: bool = False,
        separators: tuple[str, str] | None = None,
        default: Any | None = None,
    ) -> None:
        """
        Initialize a JSONResponse with serialized JSON content.

        Parameters
        ----------
        content : Any
            Content to serialize as JSON.
        status_code : HTTPStatus | int, optional
            HTTP status code for the response.
        headers : Mapping[str, str] | None, optional
            Response headers to include.
        background : BackgroundTask | None, optional
            Background task to run after response.
        indent : int | None, optional
            Indentation level for pretty-printing JSON.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters.
        separators : tuple[str, str] | None, optional
            Item and key separators for JSON output.
        default : Any | None, optional
            Custom encoder for unsupported types.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        # Store JSON serialization options for later use
        self._json_indent = indent
        self._json_ensure_ascii = ensure_ascii
        self._json_separators = separators
        self._json_default = default or self._defaultEncoder

        # Initialize the parent Response with JSON media type
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="application/json",
            background=background,
        )

        # Ensure the Content-Type header is set for JSON responses
        if not self.hasHeader("content-type"):
            self.setHeader(
                "content-type",
                "application/json; charset=utf-8",
            )

    def render(self, content: Any) -> bytes:
        """
        Serialize content to JSON bytes.

        Parameters
        ----------
        content : Any
            The content to serialize as JSON.

        Returns
        -------
        bytes
            The serialized JSON content as UTF-8 encoded bytes.

        Raises
        ------
        TypeError
            If the content cannot be serialized to JSON.
        """
        # Use orjson for fast serialization if possible
        if (
            orjson is not None
            and self._json_indent is None
            and not self._json_ensure_ascii
            and self._json_separators is None
        ):
            try:
                return orjson.dumps(
                    content,
                    default=self._json_default,
                )
            except TypeError as exc:
                error_msg = str(exc)
                raise TypeError(error_msg) from exc

        # Set default separators for compact JSON if not specified
        if self._json_separators is None and self._json_indent is None:
            separators = (",", ":")
        else:
            separators = self._json_separators

        try:
            json_string = json.dumps(
                content,
                indent=self._json_indent,
                ensure_ascii=self._json_ensure_ascii,
                separators=separators,
                default=self._json_default,
            )
        except TypeError as exc:
            error_msg = str(exc)
            raise TypeError(error_msg) from exc

        return json_string.encode("utf-8")

    def _defaultEncoder(self, obj: Any) -> Any:
        """
        Encode unsupported types for JSON serialization.

        Parameters
        ----------
        obj : Any
            The object to encode.

        Returns
        -------
        Any
            The encoded object suitable for JSON serialization.

        Raises
        ------
        TypeError
            If the object cannot be encoded for JSON serialization.
        """
        # Handle datetime, date, and time objects
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        # Handle Decimal objects
        if isinstance(obj, Decimal):
            return str(obj)
        # Handle UUID objects
        if isinstance(obj, UUID):
            return str(obj)
        # Handle Enum objects
        if isinstance(obj, Enum):
            return obj.value
        # Handle set and frozenset objects
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        # Raise error if object is not serializable
        error_msg = (
            f"Object of type {type(obj).__name__} is not JSON serializable"
        )
        raise TypeError(error_msg)

class RedirectResponse(Response):

    def __init__(
        self,
        url: str,
        status_code: HTTPStatus | int = 307,
        headers: Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Initialize a redirect response.

        Parameters
        ----------
        url : str
            Target URL for redirection.
        status_code : HTTPStatus | int, optional
            Redirect status code (301, 302, 303, 307, 308).
        headers : Mapping[str, str] | None, optional
            Optional additional headers.
        background : BackgroundTask | None, optional
            Optional background task.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Validate url type
        if not isinstance(url, str):
            error_msg = "url must be a string"
            raise TypeError(error_msg)

        # Validate status_code is a redirect code
        if not 300 <= status_code <= 399:
            error_msg = "Redirect status_code must be 3xx"
            raise ValueError(error_msg)

        # Minimal body for redirect response
        content = f"Redirecting to {url}"

        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type="text/plain",
            background=background,
        )

        # Set Location header for redirect
        self.setHeader("location", url)

        # Ensure Content-Type header is set
        if not self.hasHeader("content-type"):
            self.setHeader(
                "content-type",
                f"text/plain; charset={self.charset}",
            )

class StreamingResponse(Response):

    def __init__(
        self,
        content: AsyncIterable[bytes] | Iterable[bytes],
        status_code: HTTPStatus | int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Initialize a streaming response.

        Parameters
        ----------
        content : AsyncIterable[bytes] | Iterable[bytes]
            Streaming content source.
        status_code : HTTPStatus | int, optional
            HTTP status code for the response.
        headers : Mapping[str, str] | None, optional
            Optional response headers.
        media_type : str | None, optional
            Optional media type for the response.
        background : BackgroundTask | None, optional
            Optional background task to run after response.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        # Determine if content is async or sync iterable and wrap if needed
        if isinstance(content, AsyncIterableABC):
            stream = content
        elif isinstance(content, Iterable):
            stream = self._wrapSyncIterable(content)
        else:
            error_msg = (
                "StreamingResponse content must be "
                "AsyncIterable[bytes] or Iterable[bytes]"
            )
            raise TypeError(error_msg)

        # Initialize the parent Response with stream content
        super().__init__(
            content=stream,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

        # Ensure body is None for streaming responses
        self._body = None

        # Set Content-Type header if media_type is provided and not already set
        if media_type and not self.hasHeader("content-type"):
            self.setHeader(
                "content-type",
                f"{media_type}; charset={self.charset}"
                if media_type.startswith("text/")
                else media_type,
            )

    async def _wrapSyncIterable(
        self,
        iterable: Iterable[bytes],
    ) -> AsyncIterable[bytes]:
        """
        Adapt a synchronous iterable of bytes to an asynchronous iterable.

        Parameters
        ----------
        iterable : Iterable[bytes]
            The synchronous iterable yielding byte chunks.

        Returns
        -------
        AsyncIterable[bytes]
            An asynchronous iterable yielding byte chunks.

        Raises
        ------
        TypeError
            If any chunk in the iterable is not bytes-like.
        """
        # Yield each chunk as bytes, ensuring correct type
        for chunk in iterable:
            if not isinstance(chunk, (bytes, bytearray, memoryview)):
                error_msg = "StreamingResponse chunks must be bytes"
                raise TypeError(error_msg)
            yield bytes(chunk)

class FileResponse(StreamingResponse):

    def __init__(
        self,
        path: str | Path,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        filename: str | None = None,
        chunk_size: int = 64 * 1024,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Initialize a file streaming response.

        Parameters
        ----------
        path : str | Path
            Path to the file to serve.
        status_code : int, default=200
            HTTP status code for the response.
        headers : Mapping[str, str] | None, optional
            Optional response headers.
        media_type : str | None, optional
            Optional media type for the response.
        filename : str | None, optional
            Optional filename for Content-Disposition header.
        chunk_size : int, default=65536
            Size of file chunks to read and send.
        background : BackgroundTask | None, optional
            Optional background task to run after response.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        # Resolve the file path and validate existence and type
        self._path = Path(path)

        if not self._path.exists():
            error_msg = f"File not found: {self._path}"
            raise FileNotFoundError(error_msg)

        if not self._path.is_file():
            error_msg = f"Path is not a file: {self._path}"
            raise ValueError(error_msg)

        self._chunk_size = chunk_size

        # Guess the media type if not provided
        if media_type is None:
            guessed, _ = mimetypes.guess_type(str(self._path))
            media_type = guessed or "application/octet-stream"

        # Prepare the file stream for response
        stream = self._fileIterator()

        super().__init__(
            content=stream,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

        # Set Content-Length header for file size
        file_size = self._path.stat().st_size
        self.setHeader("content-length", str(file_size))

        # Set Content-Disposition header if filename is provided
        if filename:
            disposition = f'attachment; filename="{filename}"'
            self.setHeader("content-disposition", disposition)

    def getPath(self) -> Path:
        """
        Return the file path.

        Returns
        -------
        Path
            The path to the file being served.
        """
        return self._path

    def getFileSize(self) -> int:
        """
        Return the file size in bytes.

        Returns
        -------
        int
            The size of the file in bytes.
        """
        return self._path.stat().st_size

    async def _fileIterator(self) -> AsyncIterable[bytes]:
        """
        Yield file content in chunks asynchronously.

        Returns
        -------
        AsyncIterable[bytes]
            An asynchronous iterable yielding file chunks as bytes.
        """
        # Use the event loop to read file chunks asynchronously
        loop = asyncio.get_running_loop()

        with self._path.open("rb") as file:
            while True:
                chunk = await loop.run_in_executor(
                    None,
                    file.read,
                    self._chunk_size,
                )

                if not chunk:
                    break

                yield chunk