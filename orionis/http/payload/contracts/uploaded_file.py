from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

class IUploadedFile(ABC):
    """
    Define the contract for an uploaded file held in memory or spilled to disk.

    Implementations buffer incoming bytes via ``write()``, optionally spill
    to a temporary file, and expose the content through ``read()`` and
    ``save()``.
    """

    @property
    @abstractmethod
    def size(self) -> int:
        """Return the total number of bytes written so far."""

    @property
    @abstractmethod
    def extension(self) -> str:
        """Return the file extension derived from *filename*, in lowercase."""

    @abstractmethod
    def write(self, chunk: bytes) -> None:
        """Append *chunk* to the file buffer."""

    @abstractmethod
    def read(self) -> bytes:
        """Read the entire file content from the beginning."""

    @abstractmethod
    def replace(self, data: bytes) -> None:
        """Replace the file content with *data* and update the byte counter."""

    @abstractmethod
    def save(self, path: str | Path) -> None:
        """Write the file contents to *path* on the local filesystem."""

    @abstractmethod
    def close(self) -> None:
        """Close the file handle and release all associated resources."""
