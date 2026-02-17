import asyncio
from typing import Any
from orionis.http.response import FileResponse, Response
from orionis.support.patterns.final.meta import Final

class RSGIResponseAdapter(metaclass=Final):

    # ruff: noqa: ANN401

    async def send(
        self,
        response: Response,
        protocol: Any,
        scope: Any,
    ) -> None:
        """
        Send the HTTP response using the appropriate protocol adapter.

        Parameters
        ----------
        response : Response
            The response object to be sent.
        protocol : Any
            The protocol adapter instance.
        scope : Any
            The request scope containing metadata.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set the Server header to identify the server software.
        response.setHeader("server", "Orionis RSGI")

        status: int = response.status_code
        headers: list[tuple[str, str]] = self._convertHeaders(response)

        # Handle HEAD requests by sending an empty response.
        if scope.method == "HEAD":
            protocol.response_empty(status, headers)
            await response.runBackground()
            return

        # Handle FileResponse with support for range requests.
        if isinstance(response, FileResponse):
            file_path: str = str(response.getPath())
            file_size: int = response.getFileSize()
            range_values: tuple[int, int] | None = self._parseRange(scope, file_size)

            if range_values:
                start, end = range_values
                headers.append(
                    ("content-range", f"bytes {start}-{end-1}/{file_size}"),
                )
                headers.append(("accept-ranges", "bytes"))
                protocol.response_file_range(
                    206,
                    headers,
                    file_path,
                    start,
                    end,
                )
            else:
                protocol.response_file(
                    status,
                    headers,
                    file_path,
                )

            await response.runBackground()
            return

        # Handle streaming responses.
        if response.hasStream():
            transport = protocol.response_stream(status, headers)
            disconnect_task = asyncio.create_task(
                protocol.client_disconnect(),
            )

            async for chunk in response.getStream():
                if disconnect_task.done():
                    break
                await transport.send_bytes(chunk)

            await response.runBackground()
            return

        # Handle regular response bodies.
        body: bytes = response.getBody() or b""

        if not body:
            protocol.response_empty(status, headers)
            await response.runBackground()
            return

        if self._isTextResponse(response):
            protocol.response_str(
                status,
                headers,
                body.decode(response.charset),
            )
        else:
            protocol.response_bytes(
                status,
                headers,
                body,
            )

        await response.runBackground()

    def _convertHeaders(
        self,
        response: Response,
    ) -> list[tuple[str, str]]:
        """
        Convert raw response headers to a list of string tuples.

        Parameters
        ----------
        response : Response
            The response object containing raw headers.

        Returns
        -------
        list of tuple of str
            The converted headers as (key, value) pairs.
        """
        return [
            (k.decode("latin-1"), v.decode("latin-1"))
            for k, v in response.getRawHeaders()
        ]

    def _isTextResponse(
        self,
        response: Response,
    ) -> bool:
        """
        Determine if the response should be treated as text.

        Parameters
        ----------
        response : Response
            The response object to check.

        Returns
        -------
        bool
            True if the response is text-based, False otherwise.
        """
        if response.media_type is None:
            return False

        return (
            response.media_type.startswith("text/")
            or response.media_type == "application/json"
            or response.media_type.endswith("+json")
        )

    def _parseRange(
        self,
        scope: Any,
        file_size: int,
    ) -> tuple[int, int] | None:
        """
        Parse the Range header from the request scope.

        Parameters
        ----------
        scope : Any
            The request scope containing headers.
        file_size : int
            The total size of the file.

        Returns
        -------
        tuple of int or None
            The (start, end) byte range if valid, otherwise None.
        """
        range_header: str | None = scope.headers.get("range")
        if not range_header:
            return None

        if not range_header.startswith("bytes="):
            return None

        try:
            range_value: str = range_header.replace("bytes=", "")
            start_str, end_str = range_value.split("-")

            start: int = int(start_str) if start_str else 0
            end: int = int(end_str) + 1 if end_str else file_size

            start = max(0, start)
            end = min(end, file_size)

            if start >= end:
                return None

            return start, end

        except ValueError:
            # Return None if parsing fails.
            return None
