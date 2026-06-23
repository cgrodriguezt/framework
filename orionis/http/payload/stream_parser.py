from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.http.payload.contracts.stream_parser import IMultipartStreamParser
from orionis.http.payload.form_data import FormData
from orionis.http.payload.part import MultipartPart

if TYPE_CHECKING:
    from collections.abc import AsyncIterable

# Integer constants for the parser state machine.
_STATE_SEARCH_BOUNDARY: int = 0
_STATE_READ_HEADERS: int = 1
_STATE_READ_BODY: int = 2

# Byte values for RFC 2046 protocol characters.
_BYTE_CR: int = ord("\r")
_BYTE_LF: int = ord("\n")
_BYTE_DASH: int = ord("-")

class MultipartStreamParser(IMultipartStreamParser):
    """Parse a multipart byte stream into form fields and uploaded files."""

    __slots__ = (
        "_boundary_len",
        "boundary",
        "buffer",
        "current_part_size",
        "fields_count",
        "files_count",
        "max_fields",
        "max_files",
        "max_part_size",
        "memory_threshold",
        "stream",
    )

    def __init__(  # noqa: PLR0913
        self,
        stream: AsyncIterable[bytes],
        boundary: bytes,
        *,
        max_files: int = 1000,
        max_fields: int = 1000,
        max_part_size: int = 1024 * 1024 * 10,
        memory_threshold: int = 1024 * 1024,
    ) -> None:
        """
        Initialize a new ``MultipartStreamParser`` instance.

        Parameters
        ----------
        stream : AsyncIterable[bytes]
            Async byte stream produced by the transport layer.
        boundary : bytes
            Raw multipart boundary token (without leading ``--``).
        max_files : int, optional
            Maximum number of file parts accepted (default 1 000).
        max_fields : int, optional
            Maximum number of field parts accepted (default 1 000).
        max_part_size : int, optional
            Maximum byte size of a single part (default 10 MiB).
        memory_threshold : int, optional
            Bytes before a file part spills to disk (default 1 MiB).

        Returns
        -------
        None
        """
        # Store the async stream for deferred consumption.
        self.stream = stream
        # Build the RFC 2046 delimiter (boundary prefixed with "--").
        self.boundary = b"--" + boundary
        # Allocate the working buffer for incoming byte chunks.
        self.buffer = bytearray()
        # Apply resource-exhaustion limits.
        self.max_files = max_files
        self.max_fields = max_fields
        self.max_part_size = max_part_size
        self.memory_threshold = memory_threshold
        # Initialize runtime counters to zero.
        self.files_count = 0
        self.fields_count = 0
        self.current_part_size = 0
        # Cache boundary length to avoid recomputing it inside the hot loop.
        self._boundary_len: int = len(self.boundary)

    async def parse(self) -> FormData:  # NOSONAR  # noqa: C901, PLR0912, PLR0915
        """
        Parse the multipart stream and return all form fields and files.

        Returns
        -------
        FormData
            Container holding all parsed field values and uploaded files.
        """
        # Initialize result accumulator, active part reference, and state.
        form_items: list[tuple[str, object]] = []
        current_part: MultipartPart | None = None
        state: int = _STATE_SEARCH_BOUNDARY

        # Cache hot attributes as locals to reduce per-iteration lookups.
        buf = self.buffer
        boundary = self.boundary
        boundary_len = self._boundary_len
        max_files = self.max_files
        max_fields = self.max_fields
        max_part_size = self.max_part_size
        memory_threshold = self.memory_threshold
        files_count = self.files_count
        fields_count = self.fields_count
        curr_part_size = 0

        # Consume incoming byte chunks from the transport layer.
        async for chunk in self.stream:
            buf.extend(chunk)

            while True:
                if state == _STATE_SEARCH_BOUNDARY:
                    # Find the next RFC 2046-compliant boundary (at position 0
                    # or preceded by CRLF) to avoid false positives from preamble.
                    index = -1
                    search_start = 0
                    while True:
                        pos = buf.find(boundary, search_start)
                        if pos == -1:
                            break
                        if pos == 0 or (
                            buf[pos - 2] == _BYTE_CR and buf[pos - 1] == _BYTE_LF
                        ):
                            index = pos
                            break
                        search_start = pos + 1

                    if index == -1:
                        break

                    boundary_end = index + boundary_len
                    buf_len = len(buf)

                    # Detect the final boundary (--boundary--) to end parsing.
                    if (
                        boundary_end + 2 <= buf_len
                        and buf[boundary_end] == _BYTE_DASH
                        and buf[boundary_end + 1] == _BYTE_DASH
                    ):
                        self.files_count = files_count
                        self.fields_count = fields_count
                        return FormData(form_items)

                    # Advance past the boundary and its optional CRLF terminator.
                    skip_bytes = boundary_len
                    if (
                        boundary_end + 2 <= buf_len
                        and buf[boundary_end] == _BYTE_CR
                        and buf[boundary_end + 1] == _BYTE_LF
                    ):
                        skip_bytes += 2

                    del buf[: index + skip_bytes]
                    curr_part_size = 0
                    state = _STATE_READ_HEADERS

                elif state == _STATE_READ_HEADERS:
                    # Locate the blank line terminating the MIME header block.
                    header_end = buf.find(b"\r\n\r\n")
                    if header_end == -1:
                        break

                    # Decode header bytes and build a lowercase-keyed dict.
                    raw_headers = buf[:header_end].decode()
                    headers: dict[str, str] = {}
                    for line in raw_headers.split("\r\n"):
                        colon = line.find(":")
                        if colon != -1:
                            key = line[:colon].strip().lower()
                            headers[key] = line[colon + 1 :].strip()

                    current_part = MultipartPart(headers, memory_threshold)
                    del buf[: header_end + 4]
                    state = _STATE_READ_BODY

                elif state == _STATE_READ_BODY:
                    if current_part is None:
                        error_msg = "No current part in READ body state"
                        raise ValueError(error_msg)

                    boundary_index = buf.find(boundary)
                    if boundary_index == -1:
                        # Keep a tail of boundary_len bytes to avoid
                        # splitting a boundary across consecutive chunks.
                        safe_len = max(0, len(buf) - boundary_len)
                        if safe_len > 0:
                            if curr_part_size + safe_len > max_part_size:
                                error_msg = "Part size exceeds maximum"
                                raise ValueError(error_msg)
                            current_part.write(buf[:safe_len])
                            curr_part_size += safe_len
                            del buf[:safe_len]
                        break

                    # Strip the CRLF that precedes the boundary marker.
                    body_end = boundary_index
                    if (
                        boundary_index >= 2  # noqa: PLR2004
                        and buf[boundary_index - 2] == _BYTE_CR
                        and buf[boundary_index - 1] == _BYTE_LF
                    ):
                        body_end -= 2

                    # Validate part size before materializing the body slice.
                    if curr_part_size + body_end > max_part_size:
                        error_msg = "Part size exceeds maximum"
                        raise ValueError(error_msg)

                    if body_end:
                        current_part.write(buf[:body_end])

                    value = current_part.finalize()

                    if current_part.name is None:
                        error_msg = "Part missing name attribute"
                        raise ValueError(error_msg)

                    # Enforce file/field limits and record the completed part.
                    if current_part.is_file:
                        files_count += 1
                        if files_count > max_files:
                            error_msg = "Too many files"
                            raise ValueError(error_msg)
                    else:
                        fields_count += 1
                        if fields_count > max_fields:
                            error_msg = "Too many fields"
                            raise ValueError(error_msg)

                    form_items.append((current_part.name, value))
                    del buf[:boundary_index]
                    current_part = None
                    state = _STATE_SEARCH_BOUNDARY

        # Sync local counters back to the instance for external inspection.
        self.files_count = files_count
        self.fields_count = fields_count

        return FormData(form_items)
