from __future__ import annotations
import http.cookies
import sys
from collections.abc import Mapping
from datetime import datetime
from email.utils import format_datetime
from typing import Any, Literal
from orionis.support.background.task import BackgroundTask

class Response:

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        Initialize the Response object.

        Parameters
        ----------
        content : Any, optional
            The content to be rendered in the response.
        status_code : int, optional
            The HTTP status code for the response.
        headers : Mapping[str, str] | None, optional
            The headers to include in the response.
        media_type : str | None, optional
            The media type of the response content.
        background : BackgroundTask | None, optional
            The background task to execute after sending the response.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Validate status_code type and range
        if not isinstance(status_code, int):
            error_msg = "status_code must be an integer"
            raise TypeError(error_msg)
        if status_code < 100 or status_code > 599:
            error_msg = "status_code must be between 100 and 599"
            raise ValueError(error_msg)
        self.__status_code = status_code

        # Validate media_type type
        if not isinstance(media_type, str | None):
            error_msg = "media_type must be a string or None"
            raise TypeError(error_msg)

        self.__media_type = None
        if media_type is not None:
            self.__media_type = media_type

        # Validate background type
        if not isinstance(background, BackgroundTask | None):
            error_msg = "background must be a BackgroundTask or None"
            raise TypeError(error_msg)
        self.__background = background

        # Render response body
        self.__body = self.__renderBody(content)

        # Validate headers type and initialize headers
        if not isinstance(headers, Mapping | None):
            error_msg = "headers must be a mapping or None"
            raise TypeError(error_msg)
        self.__initHeaders(headers)

        # Set default charset for text media types
        self.__charset = "utf-8"

    def __renderBody(self, content: Any) -> bytes | memoryview:
        """
        Render response content as bytes or memoryview.

        Parameters
        ----------
        content : Any
            Content to be rendered.

        Returns
        -------
        bytes or memoryview
            Rendered content as bytes or memoryview.
        """
        if content is None:
            # Return empty bytes if no content is provided
            return b""

        if isinstance(content, (bytes, memoryview)):
            # Return content directly if already bytes or memoryview
            return content

        if isinstance(content, str):
            # Encode string content to bytes using UTF-8
            return content.encode(self.__charset)

        # Convert other types to string and encode as bytes
        return str(content).encode(self.__charset)

    def __initHeaders(self, headers: Mapping[str, str] | None = None) -> None:
        """
        Initialize response headers.

        Parameters
        ----------
        headers : Mapping[str, str] | None, optional
            Headers to include in the response.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Sets default Content-Length and Content-Type headers if not provided.
        """
        # Initialize headers and flags for default population
        if headers is None:
            response_headers: list[tuple[bytes, bytes]] = []
            populate_content_length = True
            populate_content_type = True
        else:
            response_headers = [
                (k.lower().encode("latin-1"), v.encode("latin-1"))
                for k, v in headers.items()
            ]
            keys = [h[0] for h in response_headers]
            populate_content_length = b"content-length" not in keys
            populate_content_type = b"content-type" not in keys

        # Get the response body for calculating Content-Length if needed
        body = self.__body

        # Add Content-Length header if needed and status code allows a body
        if (
            body is not None
            and populate_content_length
            and not (self.__status_code < 200 or self.__status_code in (204, 304))
        ):
            content_length = str(len(body))
            response_headers.append(
                (b"content-length", content_length.encode("latin-1"))
            )

        # Determine Content-Type header value
        content_type = self.__media_type

        # Add Content-Type header for text media types with charset if needed
        if content_type is not None and populate_content_type:
            if (
                content_type.startswith("text/") and
                "charset=" not in content_type.lower()
            ):
                content_type += "; charset=" + self.__charset
            response_headers.append(
                (b"content-type", content_type.encode("latin-1"))
            )

        self.__headers = response_headers

    @property
    def headers(self) -> MutableHeaders:
        if not hasattr(self, "_headers"):
            self._headers = MutableHeaders(raw=self.raw_headers)
        return self._headers

    def setCookie(
        self,
        key: str,
        value: str = "",
        max_age: int | None = None,
        expires: datetime | str | int | None = None,
        path: str | None = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
        partitioned: bool = False,
    ) -> None:
        cookie: http.cookies.BaseCookie[str] = http.cookies.SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]["max-age"] = max_age
        if expires is not None:
            if isinstance(expires, datetime):
                cookie[key]["expires"] = format_datetime(expires, usegmt=True)
            else:
                cookie[key]["expires"] = expires
        if path is not None:
            cookie[key]["path"] = path
        if domain is not None:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be either 'strict', 'lax' or 'none'"
            cookie[key]["samesite"] = samesite
        if partitioned:
            if sys.version_info < (3, 14):
                raise ValueError("Partitioned cookies are only supported in Python 3.14 and above.")  # pragma: no cover
            cookie[key]["partitioned"] = True  # pragma: no cover

        cookie_val = cookie.output(header="").strip()
        self.raw_headers.append((b"set-cookie", cookie_val.encode("latin-1")))

    def deleteCookie(
        self,
        key: str,
        path: str = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
    ) -> None:
        self.set_cookie(
            key,
            max_age=0,
            expires=0,
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )












    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        prefix = "websocket." if scope["type"] == "websocket" else ""
        await send(
            {
                "type": prefix + "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        await send({"type": prefix + "http.response.body", "body": self.body})

        if self.background is not None:
            await self.background()
