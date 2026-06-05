from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType
    from orionis.http.payload.uploaded_file import UploadedFile

class IFormData(ABC):
    """
    Define the contract for parsed multipart form data.

    Implementations hold ordered ``(name, value)`` pairs from a multipart
    body, support multiple values per field name, and release open file
    handles on close.
    """

    @property
    @abstractmethod
    def fields(self) -> dict[str, list[str]]:
        """Return all text field values grouped by name."""

    @property
    @abstractmethod
    def files(self) -> dict[str, list[UploadedFile]]:
        """Return all uploaded file values grouped by name."""

    @abstractmethod
    def get(self, key: str, default: object | None = None) -> object | None:
        """Return the last value for *key*, or *default*."""

    @abstractmethod
    def getAll(self, key: str) -> list[str | UploadedFile]:
        """Return every value for *key* in insertion order."""

    @abstractmethod
    def multiItems(self) -> list[tuple[str, str | UploadedFile]]:
        """Return all ``(name, value)`` pairs in insertion order."""

    @abstractmethod
    def close(self) -> None:
        """Close all uploaded file handles to release resources."""

    @abstractmethod
    def __getitem__(self, key: str) -> object:
        """Return the last value for *key* using subscript notation."""

    @abstractmethod
    def __contains__(self, key: object) -> bool:
        """Return ``True`` if at least one item with *key* exists."""

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        """Iterate over unique field names in first-seen insertion order."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of unique field names."""

    @abstractmethod
    def __repr__(self) -> str:
        """Return the canonical string representation."""

    @abstractmethod
    def __enter__(self) -> Self:
        """Enter the context manager and return this instance."""

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close all uploaded file handles."""
