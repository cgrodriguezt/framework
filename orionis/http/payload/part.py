from __future__ import annotations
import base64
import quopri
from contextlib import suppress
from urllib.parse import unquote_to_bytes
from orionis.http.payload.uploaded_file import UploadedFile
from orionis.http.payload.contracts.part import IMultipartPart

class MultipartPart(IMultipartPart):
    """Represent a single part within a multipart HTTP request body."""

    __slots__ = (
        "content_type",
        "data",
        "filename",
        "headers",
        "is_file",
        "name",
    )

    def __init__(self, headers: dict[str, str], memory_threshold: int) -> None:
        """
        Initialize a new ``MultipartPart`` from its MIME headers.

        Parameters
        ----------
        headers : dict[str, str]
            Lowercased headers for this multipart part.
        memory_threshold : int
            Maximum in-memory bytes before spilling to disk.

        Returns
        -------
        None
        """
        self.headers = headers

        # Parse Content-Disposition header for attributes.
        # _parseContentDisposition already fuses RFC 5987 extended values
        # (filename*) over plain fallbacks, so attrs["filename"] is always
        # the highest-priority value when both forms are present.
        disposition = headers.get("content-disposition", "")
        attrs = self._parseContentDisposition(disposition)

        self.name: str | None = attrs.get("name")
        self.filename: str | None = attrs.get("filename")
        self.content_type: str | None = headers.get("content-type")

        self.is_file: bool = self.filename is not None

        # Union annotation keeps both branches type-safe at the call sites.
        self.data: UploadedFile | bytearray
        if self.is_file:
            self.data = UploadedFile(
                self.filename, self.content_type, memory_threshold,
            )
        else:
            self.data = bytearray()

    def _parseContentDisposition(self, disposition: str) -> dict[str, str]:
        """
        Parse a ``Content-Disposition`` header into a key-value dict.

        Parameters
        ----------
        disposition : str
            Raw ``Content-Disposition`` header value.

        Returns
        -------
        dict[str, str]
            Lowercased attribute names mapped to unquoted values.
        """
        attrs: dict[str, str] = {}
        # Collect RFC 5987 extended values separately; they override plain
        # fallbacks regardless of token order per RFC 6266 §4.1.
        extended: dict[str, str] = {}

        for row_part in disposition.split(";"):
            part = row_part.strip()
            if "=" not in part:
                continue

            key, value = part.split("=", 1)
            key = key.strip().lower()
            value = value.strip()

            if key.endswith("*"):
                # RFC 5987: charset'language'pct-encoded-value
                plain_key = key[:-1]
                with suppress(Exception):  # NOSONAR
                    charset, _, tail = value.partition("'")
                    _, _, encoded = tail.partition("'")
                    decoded = unquote_to_bytes(encoded).decode(
                        charset.strip() or "utf-8",
                    )
                    extended[plain_key] = decoded
                continue

            # Plain attribute
            if (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            value = value.replace('\\"', '"').replace("\\'", "'")
            attrs[key] = value

        # Extended values override plain fallbacks (RFC 5987 / RFC 6266)
        attrs.update(extended)
        return attrs

    def write(self, chunk: bytes) -> None:
        """
        Append *chunk* to this part's data buffer.

        Parameters
        ----------
        chunk : bytes
            Raw bytes received from the multipart stream.

        Returns
        -------
        None
        """
        if self.is_file:
            self.data.write(chunk)  # type: ignore[union-attr]
        else:
            self.data.extend(chunk)  # type: ignore[union-attr]

    def finalize(self) -> UploadedFile | str:  # NOSONAR
        """
        Return this part's content in its final form.

        For field parts, applies ``Content-Transfer-Encoding`` decoding
        (``base64`` or ``quoted-printable``) and decodes to a string using
        the charset declared in the part's ``Content-Type`` header, falling
        back to UTF-8.

        Returns
        -------
        UploadedFile | str
            The ``UploadedFile`` handle for file parts, or the decoded
            string for field parts.
        """
        cte = self.headers.get("content-transfer-encoding", "").strip().lower()

        if not self.is_file:
            raw: bytes = bytes(self.data)  # type: ignore[arg-type]
            if cte == "base64":
                raw = base64.b64decode(raw)
            elif cte == "quoted-printable":
                raw = quopri.decodestring(raw)
            # Use per-part charset from Content-Type (falls back to utf-8)
            charset = "utf-8"
            content_type_hdr = self.headers.get("content-type", "")
            if content_type_hdr and "charset=" in content_type_hdr.lower():
                for raw_seg in content_type_hdr.split(";"):
                    seg = raw_seg.strip()
                    if seg.lower().startswith("charset="):
                        charset = seg[8:].strip().strip('"').strip("'")
                        break
            return raw.decode(charset)

        # File parts: decode CTE in-place when needed
        if cte in ("base64", "quoted-printable"):
            file_obj: UploadedFile = self.data  # type: ignore[assignment]
            raw_encoded = file_obj.read()
            decoded = (
                base64.b64decode(raw_encoded)
                if cte == "base64"
                else quopri.decodestring(raw_encoded)
            )
            file_obj.replace(decoded)

        return self.data  # type: ignore[return-value]
