import io
import tempfile
from pathlib import Path
from contextlib import suppress
from orionis.support.patterns.final.meta import Final

class UploadedFile(metaclass=Final):

    __slots__ = (
        "_file",
        "_in_memory",
        "_memory_threshold",
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
        Initialize an UploadedFile instance.

        Parameters
        ----------
        filename : str
            Name of the uploaded file.
        content_type : str | None
            MIME type of the uploaded file.
        memory_threshold : int
            Maximum size in bytes to keep file in memory before writing to disk.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.filename = filename
        self.content_type = content_type
        self._size = 0
        self._in_memory = True
        self._file = io.BytesIO()
        self._memory_threshold = memory_threshold

    def write(self, chunk: bytes) -> None:
        """
        Write a chunk of bytes to the uploaded file.

        Parameters
        ----------
        chunk : bytes
            Data to write to the file.

        Returns
        -------
        None
            This method does not return a value.
        """
        self._size += len(chunk)
        # Move to disk if memory threshold is exceeded
        if self._in_memory and self._size > self._memory_threshold:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(self._file.getvalue())
                tmp_name = tmp.name
            self._file.close()
            # Use context manager to open file and assign the file object
            with Path(tmp_name).open("ab+") as f:
                self._file = f
                self._in_memory = False
                self._file.write(chunk)
            return
        self._file.write(chunk)

    @property
    def size(self) -> int:
        """
        Return the size of the uploaded file in bytes.

        Returns
        -------
        int
            The size of the uploaded file in bytes.
        """
        return self._size

    @property
    def extension(self) -> str:
        """
        Return the file extension in lowercase.

        Returns
        -------
        str
            The file extension, including the leading dot, in lowercase.
        """
        return Path(self.filename).suffix.lower()

    def read(self) -> bytes:
        """
        Read the entire content of the uploaded file.

        Returns
        -------
        bytes
            The content of the uploaded file as bytes.
        """
        self._file.seek(0)
        return self._file.read()

    def save(self, path: str | Path) -> None:
        """
        Save the uploaded file to the specified path.

        Parameters
        ----------
        path : str | Path
            The destination path where the file will be saved.

        Returns
        -------
        None
            This method does not return a value.
        """
        path = Path(path)
        self._file.seek(0)
        # Write the file content to the specified path
        path.write_bytes(self._file.read())

    def close(self) -> None:
        """
        Close the file and remove it from disk if not in memory.

        Returns
        -------
        None
            This method does not return a value.
        """
        if hasattr(self, "_file") and self._file:
            self._file.close()
        if not self._in_memory and hasattr(self, "_file"):
            with suppress(OSError):
                Path(self._file.name).unlink()

    def __del__(self) -> None:
        """
        Clean up resources when the object is garbage collected.

        Returns
        -------
        None
            This method does not return a value.
        """
        with suppress(Exception):
            self.close()
