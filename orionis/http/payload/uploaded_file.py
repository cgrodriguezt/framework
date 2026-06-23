from __future__ import annotations
import re
import tempfile
from contextlib import suppress
from pathlib import Path
from orionis.http.payload.contracts.uploaded_file import IUploadedFile

# Forbidden filename characters on POSIX and Windows systems
_UNSAFE_FILENAME_RE = re.compile(r'[\x00-\x1f\x7f/\\:*?"<>|]')

# Pattern to detect dotfiles and path-traversal prefixes
_DOTFILE_RE = re.compile(r"^\.+")

# Maximum chunk size for streaming file saves to disk (64 KiB)
_CHUNK_SIZE = 64 * 1024

# Uploaded file container with automatic memory-to-disk spill support
class UploadedFile(IUploadedFile):
    """
    Hold an uploaded file in memory or spill it to a temporary file on disk.

    Parameters
    ----------
    filename : str
        Original name of the uploaded file as reported by the client.
    content_type : str or None
        MIME type declared by the client, or ``None`` if absent.
    memory_threshold : int, optional
        Maximum in-memory bytes before spilling to disk (default 1 MiB).
    """

    __slots__ = (
        "_extension",
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
        path-traversal sequences (leading dots) are removed. If the result
        is empty after sanitization the filename falls back to ``"upload"``.

        Parameters
        ----------
        filename : str
            Original name of the uploaded file as reported by the client.
        content_type : str or None
            MIME type declared by the client, or ``None`` if absent.
        memory_threshold : int, optional
            Maximum in-memory bytes before spilling to disk (default 1 MiB).

        Returns
        -------
        None
        """
        # Sanitize filename to block path traversal and forbidden characters
        self.filename = self._sanitizeFilename(filename)
        self.content_type = content_type
        self._size = 0
        # SpooledTemporaryFile spills to disk once memory_threshold is exceeded
        self._file = tempfile.SpooledTemporaryFile(  # noqa: SIM115
            max_size=memory_threshold,
        )
        # Compute extension once at init to avoid repeated Path object creation
        dot = self.filename.rfind(".")
        self._extension: str = self.filename[dot:].lower() if dot > 0 else ""

    @staticmethod
    def _sanitizeFilename(filename: str) -> str:
        """
        Return a safe version of *filename* suitable for use on the filesystem.

        Strips null bytes, control characters, path separators, and
        Windows-reserved characters. Removes leading dots to prevent
        dotfile or path-traversal attacks. Falls back to ``"upload"``
        when the sanitized result is empty.

        Parameters
        ----------
        filename : str
            Raw filename as supplied by the client.

        Returns
        -------
        str
            Sanitized filename safe for local persistence.
        """
        # Normalize separators and extract basename without a Path allocation
        name = filename.replace("\\", "/").rsplit("/", 1)[-1]
        # Remove characters forbidden on POSIX and Windows filesystems
        name = _UNSAFE_FILENAME_RE.sub("", name)
        # Strip leading dots to block dotfile and path-traversal inputs
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
        # Track cumulative size before writing to the spooled buffer
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
        # Return the value pre-computed at initialization
        return self._extension

    def read(self) -> bytes:
        """
        Read the entire file content from the beginning.

        Returns
        -------
        bytes
            Full file contents.
        """
        # Seek to the start to ensure full content is returned
        self._file.seek(0)
        return self._file.read()

    def replace(self, data: bytes) -> None:
        """
        Replace the file content with *data* and update the byte counter.

        Used internally after ``Content-Transfer-Encoding`` decoding
        (base64 or quoted-printable) to write the decoded payload back
        into the spooled buffer.

        Parameters
        ----------
        data : bytes
            New file content that replaces whatever was previously written.

        Returns
        -------
        None
        """
        # Seek, truncate, then write to fully replace the buffered content
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
        path : str or Path
            Destination path for the saved file.

        Returns
        -------
        None
        """
        dest = Path(path)
        # Rewind before streaming to ensure all buffered data is written
        self._file.seek(0)
        with dest.open("wb") as fh:
            # Write in fixed-size chunks to bound peak memory usage
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
        # SpooledTemporaryFile handles both in-memory and on-disk cleanup
        self._file.close()

    def __del__(self) -> None:
        """
        Release resources when the object is garbage collected.

        Returns
        -------
        None
        """
        # Suppress all exceptions to avoid disrupting the GC cycle
        with suppress(Exception):
            self.close()
