from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.http.payload.form_data import FormData
from orionis.http.payload.part import MultipartPart
from orionis.support.patterns.final.meta import Final

if TYPE_CHECKING:
    from collections.abc import AsyncIterable

class MultipartStreamParser(metaclass=Final):
    """Parse a multipart byte stream into form fields and uploaded files."""

    __slots__ = (
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
        Initialize a new ``MultipartStreamParser``.

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
        self.stream = stream
        self.boundary = b"--" + boundary
        self.buffer = bytearray()
        self.max_files = max_files
        self.max_fields = max_fields
        self.max_part_size = max_part_size
        self.memory_threshold = memory_threshold
        self.files_count = 0
        self.fields_count = 0
        self.current_part_size = 0

    async def parse(self) -> FormData:  # NOSONAR  # noqa: C901, PLR0912, PLR0915
        """
        Parse the multipart stream and return all form fields and files.

        Returns
        -------
        FormData
            Container holding all parsed field values and uploaded files.
        """
        form_items: list[tuple[str, object]] = []

        current_part: MultipartPart | None = None
        state: str = "SEARCH_BOUNDARY"

        async for chunk in self.stream:
            self.buffer.extend(chunk)

            while True:
                if state == "SEARCH_BOUNDARY":
                    # Find the next RFC 2046-compliant boundary occurrence.
                    # A valid boundary must be at position 0 (start of stream
                    # / immediately after the previous boundary was consumed)
                    # or be preceded by \r\n.  This prevents false positives
                    # caused by preamble text that happens to contain the
                    # boundary token.
                    index = -1
                    search_start = 0
                    while True:
                        pos = self.buffer.find(self.boundary, search_start)
                        if pos == -1:
                            break
                        if pos == 0 or self.buffer[pos - 2 : pos] == b"\r\n":
                            index = pos
                            break
                        search_start = pos + 1

                    if index == -1:
                        break

                    # Check if it's the final boundary (--boundary--)
                    boundary_end = index + len(self.boundary)
                    if (
                        boundary_end + 2 <= len(self.buffer)
                        and self.buffer[boundary_end : boundary_end + 2] == b"--"
                    ):
                        # Final boundary found, parsing complete
                        return FormData(form_items)

                    # Skip CRLF after boundary if present
                    skip_bytes = len(self.boundary)
                    if (
                        boundary_end + 2 <= len(self.buffer)
                        and self.buffer[boundary_end : boundary_end + 2] == b"\r\n"
                    ):
                        skip_bytes += 2

                    # Remove preamble and boundary from buffer
                    del self.buffer[: index + skip_bytes]
                    self.current_part_size = 0
                    state = "READ_HEADERS"

                elif state == "READ_HEADERS":
                    # Look for the end of headers
                    header_end = self.buffer.find(b"\r\n\r\n")
                    if header_end == -1:
                        break

                    # Parse headers into a dictionary
                    raw_headers = self.buffer[:header_end].decode()
                    headers: dict[str, str] = {}

                    for line in raw_headers.split("\r\n"):
                        if ":" in line:
                            k, v = line.split(":", 1)
                            headers[k.strip().lower()] = v.strip()

                    current_part = MultipartPart(headers, self.memory_threshold)

                    del self.buffer[: header_end + 4]
                    state = "READ_BODY"

                elif state == "READ_BODY":
                    if current_part is None:
                        error_msg = "No current part in READ body state"
                        raise ValueError(error_msg)

                    # Look for the next boundary to determine the end of the part
                    boundary_index = self.buffer.find(self.boundary)
                    if boundary_index == -1:
                        # Write all but the possible boundary overlap to the part
                        safe_len = max(0, len(self.buffer) - len(self.boundary))
                        if safe_len > 0:
                            # Validate part size
                            if self.current_part_size + safe_len > self.max_part_size:
                                error_msg = "Part size exceeds maximum"
                                raise ValueError(error_msg)

                            current_part.write(self.buffer[:safe_len])
                            self.current_part_size += safe_len
                            del self.buffer[:safe_len]
                        break

                    # Find actual end of body (before CRLF)
                    body_end = boundary_index
                    if (
                        boundary_index >= 2  # noqa: PLR2004
                        and self.buffer[boundary_index - 2 : boundary_index] == b"\r\n"
                    ):
                        body_end -= 2

                    # Validate part size
                    body_chunk = self.buffer[:body_end]
                    if self.current_part_size + len(body_chunk) > self.max_part_size:
                        error_msg = "Part size exceeds maximum"
                        raise ValueError(error_msg)

                    # Write the part body up to the boundary
                    if body_chunk:
                        current_part.write(body_chunk)

                    value = current_part.finalize()

                    if current_part.name is None:
                        error_msg = "Part missing name attribute"
                        raise ValueError(error_msg)

                    if current_part.is_file:
                        self.files_count += 1
                        if self.files_count > self.max_files:
                            error_msg = "Too many files"
                            raise ValueError(error_msg)
                    else:
                        self.fields_count += 1
                        if self.fields_count > self.max_fields:
                            error_msg = "Too many fields"
                            raise ValueError(error_msg)
                    form_items.append((current_part.name, value))

                    del self.buffer[:boundary_index]
                    current_part = None
                    state = "SEARCH_BOUNDARY"

        return FormData(form_items)
