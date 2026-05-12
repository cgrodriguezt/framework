from __future__ import annotations
import re
import tempfile
from contextlib import suppress
from pathlib import Path
from orionis.http.payload.contracts.uploaded_file import IUploadedFile

# Characters forbidden in filenames on both POSIX and Windows.
_UNSAFE_FILENAME_RE = re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]')

# Dotfile / path-traversal prefixes.
_DOTFILE_RE = re.compile(r"^\.+")

# Maximum chunk size for streaming file saves to disk.
_CHUNK_SIZE = 64 * 1024  # 64 KiB

class UploadedFile(IUploadedFile):
    """Hold an uploaded file in memory or spill it to a temporary file on disk."""

    __slots__ = (
        "_file",
        "_size",
        "content_type",
        "filename",
    )

    def __init__(
        self,
        filename: str,
        content_type: str | None,
        memory_threshold: int = 1024 * 1024,
    ) -> None:
        """
        Initialize a new ``UploadedFile`` for an incoming multipart part.

        The *filename* is sanitized on ingestion: control characters, path
        separators, and Windows-reserved characters are stripped, and
        path-traversal sequences (leading dots) are removed.  If the result
        is empty after sanitization the filename falls back to ``"upload"``.

        Parameters
        ----------
        filename : str
            Original name of the uploaded file as reported by the client.
        content_type : str | None
            MIME type declared by the client, or ``None`` if absent.
        memory_threshold : int, optional
            Maximum in-memory bytes before spilling to disk (default 1 MiB).

        Returns
        -------
        None
        """
        self.filename = self._sanitizeFilename(filename)
        self.content_type = content_type
        self._size = 0
        self._file = tempfile.SpooledTemporaryFile(max_size=memory_threshold)  # noqa: SIM115

    @staticmethod
    def _sanitizeFilename(filename: str) -> str:
        """
        Return a safe version of *filename* suitable for use on the filesystem.

        Strips null bytes, control characters, path separators, and
        Windows-reserved characters.  Removes leading dots to prevent dotfile
        / path-traversal attacks.  Falls back to ``"upload"`` when the
        sanitized result is empty.

        Parameters
        ----------
        filename : str
            Raw filename as supplied by the client.

        Returns
        -------
        str
            Sanitized filename safe for local persistence.
        """
        # Keep only the basename — discard any directory component.
        name = Path(filename).name
        # Strip forbidden characters.
        name = _UNSAFE_FILENAME_RE.sub("", name)
        # Remove leading dots (dotfiles / path-traversal).
        name = _DOTFILE_RE.sub("", name)
        return name or "upload"

    def write(self, chunk: bytes) -> None:
        """
        Append *chunk* to the file buffer.

        ``SpooledTemporaryFile`` spills to a real temp file on disk
        automatically once *memory_threshold* bytes are exceeded.

        Parameters
        ----------
        chunk : bytes
            Raw bytes to append.

        Returns
        -------
        None
        """
        self._size += len(chunk)
        self._file.write(chunk)

    @property
    def size(self) -> int:
        """
        Return the total number of bytes written so far.

        Returns
        -------
        int
            Cumulative byte count across all ``write`` calls.
        """
        return self._size

    @property
    def extension(self) -> str:
        """
        Return the file extension derived from *filename*, in lowercase.

        Returns
        -------
        str
            Lowercase suffix including the leading dot (e.g. ``".png"``).
            Empty string if the filename has no extension.
        """
        return Path(self.filename).suffix.lower()

    def read(self) -> bytes:
        """
        Read the entire file content from the beginning.

        Returns
        -------
        bytes
            Full file contents.
        """
        self._file.seek(0)
        return self._file.read()

    def replace(self, data: bytes) -> None:
        """
        Replace the file content with *data* and update the byte counter.

        Used internally after ``Content-Transfer-Encoding`` decoding
        (base64 / quoted-printable) to write the decoded payload back
        into the spooled buffer.

        Parameters
        ----------
        data : bytes
            New file content that replaces whatever was previously written.

        Returns
        -------
        None
        """
        self._file.seek(0)
        self._file.truncate(0)
        self._file.write(data)
        self._size = len(data)

    def save(self, path: str | Path) -> None:
        """
        Write the file contents to *path* on the local filesystem.

        Streams the data in ``_CHUNK_SIZE`` (64 KiB) chunks so that large
        uploads are never loaded entirely into memory.

        Parameters
        ----------
        path : str | Path
            Destination path for the saved file.

        Returns
        -------
        None
        """
        dest = Path(path)
        self._file.seek(0)
        with dest.open("wb") as fh:
            while True:
                chunk = self._file.read(_CHUNK_SIZE)
                if not chunk:
                    break
                fh.write(chunk)

    def close(self) -> None:
        """
        Close the file handle and release all associated resources.

        ``SpooledTemporaryFile`` removes the backing temp file on close
        automatically, so no manual unlink is required.

        Returns
        -------
        None
        """
        if hasattr(self, "_file") and self._file:
            self._file.close()

    def __del__(self) -> None:
        """
        Release resources when the object is garbage collected.

        Returns
        -------
        None
        """
        with suppress(Exception):
            self.close()
